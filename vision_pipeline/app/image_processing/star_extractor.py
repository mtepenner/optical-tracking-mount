"""Star extractor - identifies bright pixels (centroids) of stars in astronomical images."""

import logging
from dataclasses import dataclass
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class StarCentroid:
    """A detected star centroid with sub-pixel position and flux."""
    x: float
    y: float
    flux: float
    fwhm: float = 0.0
    snr: float = 0.0


class StarExtractor:
    """Extracts star centroids from astronomical images.

    Uses thresholding and connected-component analysis followed by
    intensity-weighted centroid refinement for sub-pixel accuracy.
    """

    def __init__(
        self,
        detection_sigma: float = 5.0,
        min_area: int = 3,
        max_area: int = 200,
        saturation_limit: int = 60000,
    ):
        self.detection_sigma = detection_sigma
        self.min_area = min_area
        self.max_area = max_area
        self.saturation_limit = saturation_limit

    def extract(self, image: np.ndarray) -> List[StarCentroid]:
        """Extract star centroids from an image.

        Args:
            image: 2D numpy array (background-subtracted recommended)

        Returns:
            List of StarCentroid objects sorted by flux (brightest first)
        """
        img = image.astype(np.float64)
        h, w = img.shape[:2]

        # Compute detection threshold
        median_val = np.median(img)
        std_val = np.std(img)
        threshold = median_val + self.detection_sigma * std_val

        # Create binary mask of pixels above threshold
        binary = img > threshold

        # Connected component labeling (simple flood-fill approach)
        labels = self._label_components(binary)
        n_labels = int(labels.max())

        centroids: List[StarCentroid] = []

        for label_id in range(1, n_labels + 1):
            mask = labels == label_id
            area = int(np.sum(mask))

            # Filter by area
            if area < self.min_area or area > self.max_area:
                continue

            # Check for saturation
            region_max = np.max(img[mask])
            if region_max >= self.saturation_limit:
                continue

            # Compute intensity-weighted centroid
            ys, xs = np.where(mask)
            weights = img[ys, xs]
            total_flux = float(np.sum(weights))

            if total_flux <= 0:
                continue

            cx = float(np.sum(xs * weights) / total_flux)
            cy = float(np.sum(ys * weights) / total_flux)

            # Estimate FWHM from second moments
            dx = xs - cx
            dy = ys - cy
            var_x = float(np.sum(weights * dx * dx) / total_flux)
            var_y = float(np.sum(weights * dy * dy) / total_flux)
            sigma = np.sqrt((var_x + var_y) / 2.0)
            fwhm = 2.355 * sigma  # FWHM = 2.355 * sigma for Gaussian

            # Signal-to-noise ratio
            snr = float(region_max / std_val) if std_val > 0 else 0.0

            centroids.append(StarCentroid(
                x=cx, y=cy, flux=total_flux, fwhm=fwhm, snr=snr
            ))

        # Sort by flux (brightest first)
        centroids.sort(key=lambda s: s.flux, reverse=True)
        logger.info("Extracted %d star centroids", len(centroids))
        return centroids

    @staticmethod
    def _label_components(binary: np.ndarray) -> np.ndarray:
        """Simple connected-component labeling using flood fill (4-connected)."""
        h, w = binary.shape
        labels = np.zeros((h, w), dtype=np.int32)
        current_label = 0

        for i in range(h):
            for j in range(w):
                if binary[i, j] and labels[i, j] == 0:
                    current_label += 1
                    # Flood fill using stack
                    stack = [(i, j)]
                    while stack:
                        cy, cx = stack.pop()
                        if cy < 0 or cy >= h or cx < 0 or cx >= w:
                            continue
                        if not binary[cy, cx] or labels[cy, cx] != 0:
                            continue
                        labels[cy, cx] = current_label
                        stack.extend([(cy - 1, cx), (cy + 1, cx),
                                      (cy, cx - 1), (cy, cx + 1)])

        return labels
