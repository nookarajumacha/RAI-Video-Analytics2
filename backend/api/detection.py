"""Detection API endpoints.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import cv2
import numpy as np

from backend.detection.detector import detection_service
from backend.alerts.alert_manager import alert_manager

router = APIRouter(prefix="/api/detection", tags=["detection"])

@router.get("/status")
def get_detection_status():
    info = detection_service.detector.get_model_info()
    return {
        "ai_status": "RUNNING" if info.get("is_loaded") else "STANDBY",
        "model_type": info.get("type"),
        "model_path": info.get("model_path"),
        "classes_count": info.get("classes_count"),
        "monitored_threats": ["Firearm", "Knife"],
        "confidence_threshold": alert_manager.confidence_threshold
    }

@router.post("/detect-frame")
async def detect_frame(file: UploadFile = File(...)):
    """Upload a static image to test the detection pipeline."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image file format.")

    result = detection_service.process_frame(
        frame=frame,
        confidence_threshold=alert_manager.confidence_threshold
    )

    if result["detections"]:
        alert_manager.process_threats(result["detections"], source="file_upload")

    return result
