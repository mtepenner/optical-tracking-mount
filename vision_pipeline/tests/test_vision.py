"""Tests for the star centroid extraction algorithms."""

import sys
import os
import numpy as np
import pytest

# Add vision_pipeline to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.camera.zwo_asi_driver import ZWOASIDriver, CameraConfig, CameraFrame
from app.image_processing.background_subtraction import BackgroundSubtractor
from app.image_processing.star_extractor import StarExtractor, StarCentroid
from app.solver.astrometry_engine import AstrometryEngine, CelestialCoordinate


class TestCameraDriver:
    """Tests for the ZWO ASI camera driver."""

    def test_simulated_connect(self):
        driver = ZWOASIDriver(simulate=True)
        assert driver.connect() is True
        assert driver.is_connected is True

    def test_simulated_disconnect(self):
        driver = ZWOASIDriver(simulate=True)
        driver.connect()
        driver.disconnect()
        assert driver.is_connected is False

    def test_capture_without_connect(self):
        driver = ZWOASIDriver(simulate=True)
        frame = driver.capture_frame()
        assert frame is None

    def test_simulated_capture(self):
        driver = ZWOASIDriver(simulate=True)
        driver.connect()
        frame = driver.capture_frame()
        assert frame is not None
        assert isinstance(frame, CameraFrame)
        assert frame.data.shape == (1096, 1936)
        assert frame.data.dtype == np.uint16

    def test_simulated_frame_has_stars(self):
        driver = ZWOASIDriver(simulate=True)
        driver.connect()
        frame = driver.capture_frame()
        # The simulated frame should have bright pixels (stars)
        assert np.max(frame.data) > 10000

    def test_set_exposure(self):
        driver = ZWOASIDriver(simulate=True)
        driver.set_exposure(50000)
        assert driver.config.exposure_us == 50000
        driver.set_exposure(-1)
        assert driver.config.exposure_us == 1

    def test_set_gain(self):
        driver = ZWOASIDriver(simulate=True)
        driver.set_gain(300)
        assert driver.config.gain == 300
        driver.set_gain(999)
        assert driver.config.gain == 600


class TestBackgroundSubtraction:
    """Tests for the background subtraction module."""

    def test_uniform_background(self):
        bg_sub = BackgroundSubtractor(box_size=32)
        image = np.full((128, 128), 1000, dtype=np.uint16)
        background = bg_sub.estimate_background(image)
        # Background should be close to 1000
        assert abs(np.mean(background) - 1000) < 50

    def test_subtraction_removes_background(self):
        bg_sub = BackgroundSubtractor(box_size=32)
        # Create image with uniform bg + a bright spot
        image = np.full((128, 128), 500, dtype=np.uint16)
        image[64, 64] = 30000
        result = bg_sub.subtract(image)
        # The bright spot should remain prominent
        assert result[64, 64] > result[0, 0]

    def test_output_shape_matches_input(self):
        bg_sub = BackgroundSubtractor()
        image = np.random.randint(0, 5000, (256, 256), dtype=np.uint16)
        result = bg_sub.subtract(image)
        assert result.shape == image.shape
        assert result.dtype == image.dtype

    def test_sigma_clipped_median(self):
        bg_sub = BackgroundSubtractor()
        data = np.array([100, 101, 99, 102, 98, 10000])  # one outlier
        median = bg_sub._sigma_clipped_median(data)
        # Should be close to 100, not skewed by outlier
        assert abs(median - 100) < 5


class TestStarExtractor:
    """Tests for the star centroid extraction."""

    def _make_star_image(self):
        """Create a synthetic image with known star positions."""
        h, w = 200, 200
        image = np.zeros((h, w), dtype=np.uint16)
        # Add background noise
        rng = np.random.default_rng(42)
        image = (rng.normal(loc=300, scale=30, size=(h, w))).astype(np.float64)

        # Add stars at known positions
        yy, xx = np.mgrid[0:h, 0:w]
        stars = [(50, 50, 40000), (100, 150, 30000), (150, 80, 20000)]
        for sy, sx, brightness in stars:
            sigma = 2.5
            gaussian = brightness * np.exp(-((xx - sx)**2 + (yy - sy)**2) / (2 * sigma**2))
            image += gaussian

        return np.clip(image, 0, 65535).astype(np.uint16), stars

    def test_extract_finds_stars(self):
        extractor = StarExtractor(detection_sigma=5.0)
        image, expected_stars = self._make_star_image()
        centroids = extractor.extract(image)
        assert len(centroids) >= 3

    def test_centroids_near_true_positions(self):
        extractor = StarExtractor(detection_sigma=5.0)
        image, expected_stars = self._make_star_image()
        centroids = extractor.extract(image)
        # Check that each expected star has a centroid nearby
        for sy, sx, _ in expected_stars:
            found = False
            for c in centroids:
                if abs(c.x - sx) < 3 and abs(c.y - sy) < 3:
                    found = True
                    break
            assert found, f"No centroid found near ({sx}, {sy})"

    def test_centroids_sorted_by_flux(self):
        extractor = StarExtractor(detection_sigma=5.0)
        image, _ = self._make_star_image()
        centroids = extractor.extract(image)
        for i in range(len(centroids) - 1):
            assert centroids[i].flux >= centroids[i + 1].flux

    def test_empty_image_no_stars(self):
        extractor = StarExtractor(detection_sigma=5.0)
        image = np.full((100, 100), 300, dtype=np.uint16)
        centroids = extractor.extract(image)
        assert len(centroids) == 0

    def test_centroid_has_positive_snr(self):
        extractor = StarExtractor(detection_sigma=5.0)
        image, _ = self._make_star_image()
        centroids = extractor.extract(image)
        for c in centroids:
            assert c.snr > 0

    def test_label_components(self):
        binary = np.zeros((10, 10), dtype=bool)
        binary[2:4, 2:4] = True
        binary[7:9, 7:9] = True
        labels = StarExtractor._label_components(binary)
        assert labels.max() == 2


class TestAstrometryEngine:
    """Tests for the plate solving engine."""

    def test_solve_with_sufficient_stars(self):
        engine = AstrometryEngine()
        stars = [(100, 100, 50000), (200, 150, 40000), (300, 50, 30000), (150, 300, 25000)]
        solution = engine.solve(stars, 1936, 1096)
        assert solution is not None
        assert solution.confidence > 0

    def test_solve_fails_with_too_few_stars(self):
        engine = AstrometryEngine()
        stars = [(100, 100, 50000)]
        solution = engine.solve(stars, 1936, 1096)
        assert solution is None

    def test_celestial_coordinate_string(self):
        coord = CelestialCoordinate(14, 29, 0.0, 19, 31, 0.0)
        s = str(coord)
        assert "14h" in s
        assert "29m" in s

    def test_angular_separation_same_point(self):
        sep = AstrometryEngine.angular_separation(180.0, 45.0, 180.0, 45.0)
        assert abs(sep) < 1e-10

    def test_angular_separation_poles(self):
        sep = AstrometryEngine.angular_separation(0.0, 90.0, 0.0, -90.0)
        assert abs(sep - 180.0) < 1e-6

    def test_celestial_coordinate_decimal(self):
        coord = CelestialCoordinate(14, 15, 39.7, 19, 10, 56.7)
        assert abs(coord.ra_decimal_hours - 14.261) < 0.01
        assert abs(coord.dec_decimal_degrees - 19.182) < 0.01


class TestFullPipeline:
    """Integration tests for the complete vision pipeline."""

    def test_end_to_end_simulated(self):
        """Test the full pipeline from capture to plate solve."""
        from app.main import VisionPipelineService

        pipeline = VisionPipelineService(simulate=True)
        assert pipeline.initialize() is True

        result = pipeline.process_frame()
        assert "error" not in result
        assert result["stars_detected"] > 0
        assert result["solution"] is not None
        assert result["solution"]["confidence"] > 0

        pipeline.stop()

    def test_multiple_frames(self):
        """Test processing multiple frames sequentially."""
        from app.main import VisionPipelineService

        pipeline = VisionPipelineService(simulate=True)
        pipeline.initialize()

        for _ in range(3):
            result = pipeline.process_frame()
            assert "error" not in result

        pipeline.stop()
