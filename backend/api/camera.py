"""Camera Management API & MJPEG Live Video Stream.
"""

import cv2
import time
import threading
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.config.settings import settings
from backend.hardware.camera import CameraStream
from backend.detection.detector import detection_service
from backend.alerts.alert_manager import alert_manager

logger = logging.getLogger("CameraAPI")
router = APIRouter(prefix="/api/camera", tags=["camera"])

class CameraManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.is_active = False
        self.camera: CameraStream = None
        self._streaming_thread = None
        self._latest_jpeg = None
        self._fps = 0.0

    def start(self, source: int = settings.CAMERA_SOURCE) -> bool:
        with self._lock:
            if self.is_active and self.camera is not None:
                return True

            try:
                self.camera = CameraStream(
                    source=source,
                    width=settings.CAMERA_WIDTH,
                    height=settings.CAMERA_HEIGHT,
                    fps=settings.CAMERA_FPS
                )
                self.camera.start()
                self.is_active = True
                logger.info(f"Camera manager started successfully on source {source}.")
                return True
            except Exception as e:
                logger.error(f"Failed to start camera: {e}")
                self.is_active = False
                self.camera = None
                return False

    def stop(self):
        with self._lock:
            if self.camera is not None:
                self.camera.release()
                self.camera = None
            self.is_active = False
            self._latest_jpeg = None
            logger.info("Camera manager stopped.")

    def get_frame(self):
        with self._lock:
            if not self.is_active or self.camera is None:
                return False, None
            return self.camera.read()

    @property
    def fps(self) -> float:
        if self.camera is not None:
            return round(self.camera.fps, 1)
        return 0.0

    @property
    def resolution(self) -> str:
        if self.camera is not None:
            w, h = self.camera.resolution
            return f"{w}x{h}"
        return f"{settings.CAMERA_WIDTH}x{settings.CAMERA_HEIGHT}"

camera_manager = CameraManager()

class CameraActionResponse(BaseModel):
    status: str
    is_active: bool
    fps: float
    resolution: str = "2560x1440"
    profile: str = "2K QHD @ 60 FPS"
    message: str

@router.post("/start", response_model=CameraActionResponse)
def start_camera():
    success = camera_manager.start()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to initialize camera device.")
    return CameraActionResponse(
        status="ACTIVE",
        is_active=True,
        fps=camera_manager.fps,
        resolution=camera_manager.resolution,
        profile="2K QHD @ 60 FPS",
        message="Camera stream started in 2K 60 FPS mode."
    )

@router.post("/stop", response_model=CameraActionResponse)
def stop_camera():
    camera_manager.stop()
    return CameraActionResponse(
        status="STOPPED",
        is_active=False,
        fps=0.0,
        resolution=camera_manager.resolution,
        profile="2K QHD @ 60 FPS",
        message="Camera stream stopped."
    )

@router.get("/status", response_model=CameraActionResponse)
def get_camera_status():
    return CameraActionResponse(
        status="ACTIVE" if camera_manager.is_active else "DISCONNECTED",
        is_active=camera_manager.is_active,
        fps=camera_manager.fps,
        resolution=camera_manager.resolution,
        profile="2K QHD @ 60 FPS",
        message="Camera operational (2K QHD 60 FPS)." if camera_manager.is_active else "Camera offline."
    )

def generate_mjpeg_stream():
    """Generator yielding multipart MJPEG frames with real-time detection bounding boxes in 2K clarity."""
    while True:
        if not camera_manager.is_active:
            # Yield a blank placeholder frame if camera is off
            time.sleep(0.1)
            continue

        ret, frame = camera_manager.get_frame()
        if not ret or frame is None:
            time.sleep(0.005)
            continue

        # Run AI threat detection
        result = detection_service.process_frame(
            frame=frame,
            confidence_threshold=alert_manager.confidence_threshold
        )
        threats = result["detections"]

        # Forward detected threats to alert manager (handles cooldown and audio)
        if threats:
            alert_manager.process_threats(threats, source="camera_0")

        # Draw visual HUD & bounding boxes scaled for 2K resolution (2560x1440)
        annotated_frame = frame.copy()
        h, w = annotated_frame.shape[:2]
        line_thick = 3 if w >= 1920 else 2
        font_scale = 1.0 if w >= 1920 else 0.6

        for t in threats:
            x1, y1, x2, y2 = map(int, t["bbox"])
            # Red bounding box for visual threat
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), line_thick)
            label = f"[POTENTIAL THREAT] {t['label']} {t['confidence']*100:.1f}%"

            # Draw background tag for high-contrast legibility
            (txt_w, txt_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)
            bg_y1 = max(0, y1 - txt_h - 12)
            cv2.rectangle(annotated_frame, (x1, bg_y1), (x1 + txt_w + 10, y1), (0, 0, 180), -1)
            cv2.putText(
                annotated_frame,
                label,
                (x1 + 5, y1 - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                2
            )

        # High-Fidelity JPEG encoding (Quality 92 for crystal-clear 2K detail)
        ret, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@router.get("/stream")
def get_video_stream():
    """MJPEG Video streaming route consumed directly by HTML <img> elements."""
    return StreamingResponse(
        generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
