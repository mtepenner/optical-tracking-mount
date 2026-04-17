"""Background subtraction - removes noise and light pollution from astronomical images."""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class BackgroundSubtractor:
    """Removes background noise and light pollution from astronomical images.

    Uses a combination of sigma-clipped statistics and morphological operations
    to estimate and subtract the sky background.
    """

    def __init__(self, sigma_clip: float = 3.0, box_size: int = 64, filter_size: int = 3):
        self.sigma_clip = sigma_clip
        self.box_size = box_size
        self.filter_size = filter_size

    def estimate_background(self, image: np.ndarray) -> np.ndarray:
        """Estimate the background level of an astronomical image.

        Uses a grid-based approach: divides the image into boxes, computes
        sigma-clipped median in each box, then interpolates to full resolution.
        """
        h, w = image.shape[:2]
        img = image.astype(np.float64)

        # Compute grid of background estimates
        ny = max(1, h // self.box_size)
        nx = max(1, w // self.box_size)
        bg_grid = np.zeros((ny, nx), dtype=np.float64)

        for iy in range(ny):
            for ix in range(nx):
                y0 = iy * self.box_size
                y1 = min(y0 + self.box_size, h)
                x0 = ix * self.box_size
                x1 = min(x0 + self.box_size, w)
                patch = img[y0:y1, x0:x1].flatten()

                # Sigma-clipped median
                bg_grid[iy, ix] = self._sigma_clipped_median(patch)

        # Resize background grid to full image size using bilinear interpolation
        background = self._resize_grid(bg_grid, h, w)
        return background

    def subtract(self, image: np.ndarray, background: Optional[np.ndarray] = None) -> np.ndarray:
        """Subtract background from image. Estimates background if not provided."""
        if background is None:
            background = self.estimate_background(image)

        result = image.astype(np.float64) - background
        result = np.clip(result, 0, np.finfo(np.float64).max)
        return result.astype(image.dtype)

    def _sigma_clipped_median(self, data: np.ndarray) -> float:
        """Compute the median of data after iterative sigma clipping."""
        clipped = data.copy()
        for _ in range(5):  # max iterations
            if len(clipped) == 0:
                return 0.0
            med = np.median(clipped)
            std = np.std(clipped)
            if std == 0:
                return float(med)
            mask = np.abs(clipped - med) < self.sigma_clip * std
            if np.all(mask):
                break
            clipped = clipped[mask]
        return float(np.median(clipped)) if len(clipped) > 0 else 0.0

    @staticmethod
    def _resize_grid(grid: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
        """Resize a small grid to target dimensions using bilinear interpolation."""
        gh, gw = grid.shape
        if gh == 1 and gw == 1:
            return np.full((target_h, target_w), grid[0, 0], dtype=np.float64)

        # Create coordinate maps
        y_coords = np.linspace(0, gh - 1, target_h)
        x_coords = np.linspace(0, gw - 1, target_w)

        # Bilinear interpolation
        y_floor = np.floor(y_coords).astype(int)
        x_floor = np.floor(x_coords).astype(int)
        y_ceil = np.minimum(y_floor + 1, gh - 1)
        x_ceil = np.minimum(x_floor + 1, gw - 1)

        y_frac = y_coords - y_floor
        x_frac = x_coords - x_floor

        result = np.zeros((target_h, target_w), dtype=np.float64)
        for i in range(target_h):
            for j in range(target_w):
                top_left = grid[y_floor[i], x_floor[j]]
                top_right = grid[y_floor[i], x_ceil[j]]
                bot_left = grid[y_ceil[i], x_floor[j]]
                bot_right = grid[y_ceil[i], x_ceil[j]]

                top = top_left + (top_right - top_left) * x_frac[j]
                bot = bot_left + (bot_right - bot_left) * x_frac[j]
                result[i, j] = top + (bot - top) * y_frac[i]

        return result
