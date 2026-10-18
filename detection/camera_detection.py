"""High-Performance Real-Time Visual Threat Detection Assistant.
Features:
- Up to 60 FPS camera capture via threaded DirectShow & MJPG
- Decoupled asynchronous inference loop to keep video display fluid at 60 FPS
- ByteTrack persistent tracking & multi-frame temporal confirmation
- Spoken text-to-speech warnings & tactical HUD overlay
Run directly: python detection/camera_detection.py
"""

import sys
import os
import cv2
import yaml
import time
import threading
import logging

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hardware.camera import CameraStream
from detection.detector import ThreatDetector
from alerts.notification import AlertDispatcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("CameraDetectionApp")

def load_config(config_path="config/config.yaml"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

class AsyncInferenceWorker:
    """Asynchronous worker running YOLO inference in the background so video stays at 60 FPS."""
    def __init__(self, detector: ThreatDetector):
        self.detector = detector
        self._lock = threading.Lock()
        self._frame_to_process = None
        self._latest_detections = []
        self._running = False
        self._thread = None
        self._inference_fps = 0.0

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()
        return self

    def push_frame(self, frame):
        with self._lock:
            self._frame_to_process = frame

    def get_detections(self):
        with self._lock:
            return list(self._latest_detections), self._inference_fps

    def _worker_loop(self):
        last_time = time.time()
        while self._running:
            target_frame = None
            with self._lock:
                if self._frame_to_process is not None:
                    target_frame = self._frame_to_process
                    self._frame_to_process = None

            if target_frame is None:
                time.sleep(0.005)
                continue

            t0 = time.time()
            results = self.detector.detect(target_frame)
            t_diff = time.time() - t0

            with self._lock:
                self._latest_detections = results
                if t_diff > 0:
                    self._inference_fps = 1.0 / t_diff

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

def run_live_detection():
    config = load_config()
    cam_cfg = config.get("camera", {})

    logger.info("Initializing 120 FPS Camera Stream...")
    camera = CameraStream(
        source=cam_cfg.get("source", 0),
        width=cam_cfg.get("width", 1280),
        height=cam_cfg.get("height", 720),
        fps=cam_cfg.get("fps", 120)
    )

    logger.info("Initializing High-Accuracy Threat Detector...")
    detector = ThreatDetector(config)

    logger.info("Initializing Alert & HUD System...")
    alert_dispatcher = AlertDispatcher(config)

    # Decoupled inference engine to guarantee 120 FPS UI responsiveness
    inference_worker = AsyncInferenceWorker(detector)

    try:
        camera.start()
        inference_worker.start()

        print("\n" + "="*65)
        print("  WEARABLE AI SECURITY ASSISTANT — 120 FPS ULTRA-SMOOTH MODE")
        print("  Model: Custom Fine-Tuned Threat Detector (Firearms, Knives)")
        print("  Filter: ByteTrack + Multi-Frame Temporal Confirmation")
        print("  Controls:")
        print("    [q] - Quit & Exit")
        print("    [s] - Save Manual Incident Snapshot")
        print("="*65 + "\n")

        fps_calc_time = time.time()
        frame_counter = 0
        display_fps = 120.0

        while True:
            t_loop_start = time.time()
            success, frame = camera.read()
            if not success or frame is None:
                time.sleep(0.002)
                continue

            # Pass latest frame to inference worker
            inference_worker.push_frame(frame)

            # Get current active detections and inference speed
            detections, infer_fps = inference_worker.get_detections()

            # Render tactical HUD and trigger alerts
            annotated_frame = alert_dispatcher.process_detections(
                frame=frame,
                detections=detections,
                fps=display_fps
            )

            # Draw secondary badge for 120 FPS telemetry
            h, w = frame.shape[:2]
            cv2.putText(
                annotated_frame,
                f"DISPLAY: {display_fps:.1f} FPS (120Hz) | SENSOR: {camera.fps:.1f} FPS | AI: {infer_fps:.1f} FPS",
                (w - 490, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 255),
                1,
                cv2.LINE_AA
            )

            # Display window
            cv2.imshow("Wearable AI Security Assistant - 120 FPS HUD", annotated_frame)


            # Frame rate measurement
            frame_counter += 1
            if frame_counter % 30 == 0:
                elapsed = time.time() - fps_calc_time
                if elapsed > 0:
                    display_fps = 30.0 / elapsed
                fps_calc_time = time.time()

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("Termination signal received. Exiting...")
                break
            elif key == ord('s'):
                snapshot_path = f"logs/manual_snapshot_{int(time.time())}.jpg"
                os.makedirs("logs", exist_ok=True)
                cv2.imwrite(snapshot_path, annotated_frame)
                logger.info(f"Manual snapshot saved: {snapshot_path}")

    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.error(f"Runtime error: {e}", exc_info=True)
    finally:
        inference_worker.stop()
        camera.release()
        cv2.destroyAllWindows()
        logger.info("System safely shut down.")

if __name__ == "__main__":
    run_live_detection()
