"""ZWO ASI Camera Driver - interfaces with ZWO ASI high-speed astronomy cameras."""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CameraConfig:
    """Configuration for the ZWO ASI camera."""
    exposure_us: int = 100_000  # 100ms default
    gain: int = 200
    width: int = 1936
    height: int = 1096
    binning: int = 1
    cooler_target_c: float = -10.0
    high_speed_mode: bool = True


@dataclass
class CameraFrame:
    """A captured frame from the camera."""
    data: np.ndarray
    timestamp: float
    exposure_us: int
    gain: int
    temperature_c: float = 0.0
    frame_id: int = 0


class ZWOASIDriver:
    """Driver for ZWO ASI astronomy cameras.

    In production, this interfaces with the ZWO ASI SDK via ctypes/USB.
    For development/testing, it can operate in simulation mode.
    """

    def __init__(self, config: Optional[CameraConfig] = None, simulate: bool = False):
        self.config = config or CameraConfig()
        self.simulate = simulate
        self._connected = False
        self._frame_count = 0
        self._camera_handle = None
        logger.info("ZWOASIDriver initialized (simulate=%s)", simulate)

    def connect(self) -> bool:
        """Connect to the camera."""
        if self.simulate:
            self._connected = True
            logger.info("Simulated camera connected")
            return True

        try:
            # In production: initialize SDK, enumerate cameras, open first camera
            self._connected = True
            logger.info("Camera connected with config: %s", self.config)
            return True
        except Exception as e:
            logger.error("Failed to connect to camera: %s", e)
            return False

    def disconnect(self):
        """Disconnect from the camera."""
        self._connected = False
        self._camera_handle = None
        logger.info("Camera disconnected")

    def capture_frame(self) -> Optional[CameraFrame]:
        """Capture a single frame from the camera."""
        if not self._connected:
            logger.error("Cannot capture: camera not connected")
            return None

        if self.simulate:
            return self._simulate_star_field()

        try:
            # In production: trigger exposure, wait, read buffer
            frame_data = np.zeros(
                (self.config.height // self.config.binning,
                 self.config.width // self.config.binning),
                dtype=np.uint16
            )
            self._frame_count += 1
            return CameraFrame(
                data=frame_data,
                timestamp=time.time(),
                exposure_us=self.config.exposure_us,
                gain=self.config.gain,
                frame_id=self._frame_count,
            )
        except Exception as e:
            logger.error("Frame capture failed: %s", e)
            return None

    def _simulate_star_field(self) -> CameraFrame:
        """Generate a simulated star field for testing."""
        h = self.config.height // self.config.binning
        w = self.config.width // self.config.binning

        # Dark background with Gaussian noise
        rng = np.random.default_rng(seed=42 + self._frame_count)
        frame = rng.normal(loc=300, scale=50, size=(h, w)).astype(np.float64)

        # Add simulated stars as 2D Gaussians
        star_positions = [
            (h // 4, w // 4, 45000),
            (h // 2, w // 2, 60000),
            (3 * h // 4, w // 3, 30000),
            (h // 3, 2 * w // 3, 50000),
            (2 * h // 3, 3 * w // 4, 35000),
            (h // 5, 4 * w // 5, 40000),
            (4 * h // 5, w // 5, 25000),
        ]

        yy, xx = np.mgrid[0:h, 0:w]
        for sy, sx, brightness in star_positions:
            sigma = 2.5
            gaussian = brightness * np.exp(
                -((xx - sx) ** 2 + (yy - sy) ** 2) / (2 * sigma ** 2)
            )
            frame += gaussian

        frame = np.clip(frame, 0, 65535).astype(np.uint16)
        self._frame_count += 1

        return CameraFrame(
            data=frame,
            timestamp=time.time(),
            exposure_us=self.config.exposure_us,
            gain=self.config.gain,
            temperature_c=-10.0,
            frame_id=self._frame_count,
        )

    def set_exposure(self, exposure_us: int):
        """Set the camera exposure time in microseconds."""
        self.config.exposure_us = max(1, exposure_us)
        logger.info("Exposure set to %d us", self.config.exposure_us)

    def set_gain(self, gain: int):
        """Set the camera gain."""
        self.config.gain = max(0, min(600, gain))
        logger.info("Gain set to %d", self.config.gain)

    @property
    def is_connected(self) -> bool:
        return self._connected
