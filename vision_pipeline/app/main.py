"""Main gRPC server - outputs current camera pointing coordinates."""

import logging
import sys
import time
from concurrent import futures

import numpy as np

# Conditional gRPC imports for environments where grpc is available
try:
    import grpc
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False

from app.camera.zwo_asi_driver import ZWOASIDriver, CameraConfig
from app.image_processing.background_subtraction import BackgroundSubtractor
from app.image_processing.star_extractor import StarExtractor
from app.solver.astrometry_engine import AstrometryEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class VisionPipelineService:
    """Core vision pipeline that processes camera frames and determines pointing."""

    def __init__(self, simulate: bool = True):
        self.camera = ZWOASIDriver(simulate=simulate)
        self.bg_subtractor = BackgroundSubtractor()
        self.star_extractor = StarExtractor()
        self.astrometry = AstrometryEngine(pixel_scale_hint=1.0, field_of_view_deg=2.0)
        self._running = False

    def initialize(self) -> bool:
        """Initialize the vision pipeline."""
        if not self.camera.connect():
            logger.error("Failed to connect to camera")
            return False
        logger.info("Vision pipeline initialized successfully")
        return True

    def process_frame(self) -> dict:
        """Capture and process a single frame through the full pipeline."""
        frame = self.camera.capture_frame()
        if frame is None:
            return {"error": "Failed to capture frame"}

        # Step 1: Background subtraction
        bg_subtracted = self.bg_subtractor.subtract(frame.data)

        # Step 2: Star extraction
        centroids = self.star_extractor.extract(bg_subtracted)

        # Step 3: Plate solving
        star_positions = [(c.x, c.y, c.flux) for c in centroids]
        solution = self.astrometry.solve(
            star_positions,
            frame.data.shape[1],
            frame.data.shape[0],
        )

        result = {
            "frame_id": frame.frame_id,
            "timestamp": frame.timestamp,
            "stars_detected": len(centroids),
            "centroids": [{"x": c.x, "y": c.y, "flux": c.flux, "snr": c.snr} for c in centroids[:10]],
        }

        if solution:
            result["solution"] = {
                "ra": str(solution.center),
                "ra_decimal_deg": solution.center.ra_decimal_degrees,
                "dec_decimal_deg": solution.center.dec_decimal_degrees,
                "field_width_deg": solution.field_width_deg,
                "field_height_deg": solution.field_height_deg,
                "pixel_scale_arcsec": solution.pixel_scale_arcsec,
                "matched_stars": solution.matched_stars,
                "confidence": solution.confidence,
            }
            logger.info(
                "Plate solve: %s (confidence=%.2f, matched=%d)",
                solution.center, solution.confidence, solution.matched_stars,
            )
        else:
            result["solution"] = None
            logger.warning("Plate solve failed for frame %d", frame.frame_id)

        return result

    def run_loop(self, interval_s: float = 1.0):
        """Run the vision pipeline in a continuous loop."""
        self._running = True
        logger.info("Starting vision pipeline loop (interval=%.1fs)", interval_s)

        while self._running:
            try:
                result = self.process_frame()
                if "error" not in result:
                    logger.info(
                        "Frame %d: %d stars detected",
                        result["frame_id"], result["stars_detected"],
                    )
            except Exception as e:
                logger.error("Pipeline error: %s", e)
            time.sleep(interval_s)

    def stop(self):
        """Stop the pipeline loop."""
        self._running = False
        self.camera.disconnect()
        logger.info("Vision pipeline stopped")


def serve(port: int = 50051, simulate: bool = True):
    """Start the gRPC server for the vision pipeline."""
    pipeline = VisionPipelineService(simulate=simulate)

    if not pipeline.initialize():
        logger.error("Failed to initialize pipeline")
        sys.exit(1)

    if GRPC_AVAILABLE:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
        server.add_insecure_port(f"[::]:{port}")
        server.start()
        logger.info("Vision Pipeline gRPC server started on port %d", port)

        try:
            while True:
                result = pipeline.process_frame()
                time.sleep(1.0)
        except KeyboardInterrupt:
            pipeline.stop()
            server.stop(0)
    else:
        logger.info("gRPC not available, running in standalone mode")
        try:
            pipeline.run_loop(interval_s=1.0)
        except KeyboardInterrupt:
            pipeline.stop()


if __name__ == "__main__":
    simulate_mode = "--simulate" in sys.argv or True
    serve(simulate=simulate_mode)
