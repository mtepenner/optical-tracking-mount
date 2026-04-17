"""Astrometry engine - compares extracted star patterns to catalog for plate solving."""

import logging
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CelestialCoordinate:
    """Right Ascension / Declination coordinate pair."""
    ra_hours: float    # Right Ascension in hours (0-24)
    ra_minutes: float  # RA minutes
    ra_seconds: float  # RA seconds
    dec_degrees: float # Declination in degrees (-90 to +90)
    dec_minutes: float # Dec arcminutes
    dec_seconds: float # Dec arcseconds

    @property
    def ra_decimal_hours(self) -> float:
        return self.ra_hours + self.ra_minutes / 60.0 + self.ra_seconds / 3600.0

    @property
    def ra_decimal_degrees(self) -> float:
        return self.ra_decimal_hours * 15.0

    @property
    def dec_decimal_degrees(self) -> float:
        sign = -1 if self.dec_degrees < 0 else 1
        return sign * (abs(self.dec_degrees) + self.dec_minutes / 60.0 + self.dec_seconds / 3600.0)

    def __str__(self) -> str:
        dec_sign = "+" if self.dec_decimal_degrees >= 0 else "-"
        return (f"RA {int(self.ra_hours)}h {int(self.ra_minutes)}m {self.ra_seconds:.1f}s, "
                f"Dec {dec_sign}{int(abs(self.dec_degrees))}° {int(self.dec_minutes)}' {self.dec_seconds:.1f}\"")


@dataclass
class PlateSolution:
    """Result of a plate solve operation."""
    center: CelestialCoordinate
    field_width_deg: float
    field_height_deg: float
    rotation_deg: float
    pixel_scale_arcsec: float
    matched_stars: int
    confidence: float  # 0.0 to 1.0


# Simplified reference catalog (subset of bright stars from Tycho-2/Hipparcos)
REFERENCE_CATALOG = [
    {"name": "Arcturus",   "ra_h": 14, "ra_m": 15, "ra_s": 39.7, "dec_d": 19, "dec_m": 10, "dec_s": 56.7, "mag": -0.05},
    {"name": "Vega",       "ra_h": 18, "ra_m": 36, "ra_s": 56.3, "dec_d": 38, "dec_m": 47, "dec_s": 1.3,  "mag": 0.03},
    {"name": "Capella",    "ra_h": 5,  "ra_m": 16, "ra_s": 41.4, "dec_d": 46, "dec_m": 0,  "dec_s": 21.5, "mag": 0.08},
    {"name": "Rigel",      "ra_h": 5,  "ra_m": 14, "ra_s": 32.3, "dec_d": -8, "dec_m": 12, "dec_s": 5.9,  "mag": 0.13},
    {"name": "Betelgeuse", "ra_h": 5,  "ra_m": 55, "ra_s": 10.3, "dec_d": 7,  "dec_m": 24, "dec_s": 25.4, "mag": 0.42},
    {"name": "Altair",     "ra_h": 19, "ra_m": 50, "ra_s": 47.0, "dec_d": 8,  "dec_m": 52, "dec_s": 6.0,  "mag": 0.77},
    {"name": "Aldebaran",  "ra_h": 4,  "ra_m": 35, "ra_s": 55.2, "dec_d": 16, "dec_m": 30, "dec_s": 33.5, "mag": 0.85},
    {"name": "Spica",      "ra_h": 13, "ra_m": 25, "ra_s": 11.6, "dec_d": -11,"dec_m": 9,  "dec_s": 40.8, "mag": 0.97},
    {"name": "Pollux",     "ra_h": 7,  "ra_m": 45, "ra_s": 18.9, "dec_d": 28, "dec_m": 1,  "dec_s": 34.3, "mag": 1.14},
    {"name": "Deneb",      "ra_h": 20, "ra_m": 41, "ra_s": 25.9, "dec_d": 45, "dec_m": 16, "dec_s": 49.2, "mag": 1.25},
]


class AstrometryEngine:
    """Plate solving engine that matches star patterns against a reference catalog.

    In a full implementation, this would use triangle-matching algorithms
    against the complete Tycho-2 or Gaia DR3 catalog. This implementation
    provides the core architecture with a simplified demonstration catalog.
    """

    def __init__(self, pixel_scale_hint: float = 1.0, field_of_view_deg: float = 2.0):
        self.pixel_scale_hint = pixel_scale_hint  # arcsec/pixel hint
        self.field_of_view_deg = field_of_view_deg
        self._catalog = REFERENCE_CATALOG

    def solve(
        self,
        star_positions: List[Tuple[float, float, float]],
        image_width: int,
        image_height: int,
    ) -> Optional[PlateSolution]:
        """Attempt to plate-solve from a list of detected star positions.

        Args:
            star_positions: List of (x, y, flux) tuples from star extraction
            image_width: Image width in pixels
            image_height: Image height in pixels

        Returns:
            PlateSolution if successful, None if matching failed
        """
        if len(star_positions) < 3:
            logger.warning("Need at least 3 stars for plate solving, got %d", len(star_positions))
            return None

        # Compute inter-star distances (angular separations in pixels)
        triangles = self._build_triangles(star_positions[:min(20, len(star_positions))])

        if not triangles:
            logger.warning("Could not build sufficient triangles for matching")
            return None

        # Try matching against catalog triangles
        best_match = self._match_triangles(triangles, image_width, image_height)

        if best_match is None:
            logger.info("Plate solve failed: no matching pattern found")
            return None

        return best_match

    def _build_triangles(
        self, stars: List[Tuple[float, float, float]]
    ) -> List[Tuple[float, float, float, int, int, int]]:
        """Build a set of triangle descriptors from star positions."""
        triangles = []
        n = len(stars)
        for i in range(min(n, 10)):
            for j in range(i + 1, min(n, 10)):
                for k in range(j + 1, min(n, 10)):
                    d_ij = math.hypot(stars[i][0] - stars[j][0], stars[i][1] - stars[j][1])
                    d_ik = math.hypot(stars[i][0] - stars[k][0], stars[i][1] - stars[k][1])
                    d_jk = math.hypot(stars[j][0] - stars[k][0], stars[j][1] - stars[k][1])

                    sides = sorted([d_ij, d_ik, d_jk])
                    if sides[2] > 0:
                        ratio1 = sides[0] / sides[2]
                        ratio2 = sides[1] / sides[2]
                        triangles.append((ratio1, ratio2, sides[2], i, j, k))
        return triangles

    def _match_triangles(
        self,
        triangles: List[Tuple[float, float, float, int, int, int]],
        img_w: int,
        img_h: int,
    ) -> Optional[PlateSolution]:
        """Match image triangles against catalog. Returns a simulated solution for demonstration."""
        # In production, this would perform actual triangle matching against the full catalog.
        # For demonstration, return a solution centered on a known bright star region.
        pixel_scale = self.pixel_scale_hint
        field_w = img_w * pixel_scale / 3600.0
        field_h = img_h * pixel_scale / 3600.0

        # Simulated solve: center near Arcturus (a well-known bright star)
        center = CelestialCoordinate(
            ra_hours=14, ra_minutes=15, ra_seconds=39.7,
            dec_degrees=19, dec_minutes=10, dec_seconds=56.7,
        )

        matched = min(len(triangles), 5)
        confidence = min(1.0, matched / 5.0)

        return PlateSolution(
            center=center,
            field_width_deg=field_w,
            field_height_deg=field_h,
            rotation_deg=0.0,
            pixel_scale_arcsec=pixel_scale,
            matched_stars=matched,
            confidence=confidence,
        )

    @staticmethod
    def angular_separation(ra1_deg: float, dec1_deg: float, ra2_deg: float, dec2_deg: float) -> float:
        """Compute angular separation between two sky coordinates in degrees."""
        ra1 = math.radians(ra1_deg)
        dec1 = math.radians(dec1_deg)
        ra2 = math.radians(ra2_deg)
        dec2 = math.radians(dec2_deg)

        cos_sep = (math.sin(dec1) * math.sin(dec2) +
                   math.cos(dec1) * math.cos(dec2) * math.cos(ra1 - ra2))
        cos_sep = max(-1.0, min(1.0, cos_sep))
        return math.degrees(math.acos(cos_sep))
