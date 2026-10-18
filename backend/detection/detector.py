"""Clean Model Interface & YOLO Threat Detector.
Decouples inference from the application layer to enable seamless future upgrades.
"""

import os
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np

from backend.config.settings import settings
from backend.detection.postprocessing import filter_and_classify_detections

logger = logging.getLogger("ThreatDetector")

class BaseDetector(ABC):
    """Abstract interface for any object detection backend."""
    @abstractmethod
    def infer(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        pass

class YOLOThreatDetector(BaseDetector):
    """Production YOLO-family detector implementing the BaseDetector interface."""
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.MODEL_PATH
        self.model = None
        self.is_loaded = False
        self.class_names = {}
        self._load_model()

    def _load_model(self):
        try:
            from ultralytics import YOLO

            # Check if specialized model exists; otherwise fallback to base weights
            target_path = self.model_path
            if not os.path.exists(target_path):
                if os.path.exists(settings.FALLBACK_MODEL_PATH):
                    target_path = settings.FALLBACK_MODEL_PATH
                else:
                    target_path = "yolov8n.pt"
                logger.warning(f"Specified model '{self.model_path}' not found. Falling back to: {target_path}")

            logger.info(f"Loading YOLO weights from: {target_path}")
            self.model = YOLO(target_path)
            self.class_names = self.model.names
            self.is_loaded = True
            logger.info(f"Detector initialized successfully. Detected classes: {len(self.class_names)}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}. Switching to Demo Mock Detector.")
            self.model = None
            self.is_loaded = False

    def infer(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Runs raw model inference on a single frame."""
        if not self.is_loaded or self.model is None or frame is None:
            return []

        try:
            results = self.model.predict(
                source=frame,
                conf=0.25, # Grab candidate detections; postprocessing applies user threshold
                iou=settings.IOU_THRESHOLD,
                imgsz=settings.INPUT_IMAGE_SIZE,
                verbose=False
            )
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return []

        raw_detections = []
        if not results:
            return raw_detections

        r = results[0]
        boxes = r.boxes
        if boxes is None:
            return raw_detections

        for box in boxes:
            cls_id = int(box.cls[0].item())
            cls_name = self.class_names.get(cls_id, f"class_{cls_id}").lower()
            conf = float(box.conf[0].item())
            xyxy = box.xyxy[0].tolist()

            raw_detections.append({
                "class_id": cls_id,
                "class_name": cls_name,
                "confidence": conf,
                "bbox": xyxy
            })

        return raw_detections

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "type": "Ultralytics YOLO",
            "model_path": self.model_path,
            "is_loaded": self.is_loaded,
            "classes_count": len(self.class_names),
            "classes": self.class_names
        }

class MockDemoDetector(BaseDetector):
    """Fallback detector used when running in lightweight or test environments."""
    def infer(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        # Returns empty or simulated data for testing
        return []

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "type": "MockDemoDetector",
            "model_path": "simulated",
            "is_loaded": True,
            "classes_count": 2,
            "classes": {0: "Firearm", 1: "Knife"}
        }

class ThreatDetectionService:
    """High-level service coordinating model inference, latency tracking, and threat filtering."""
    def __init__(self, detector: Optional[BaseDetector] = None):
        self.detector = detector or YOLOThreatDetector()

    def process_frame(
        self,
        frame: np.ndarray,
        confidence_threshold: float = settings.DEFAULT_CONFIDENCE_THRESHOLD
    ) -> Dict[str, Any]:
        t0 = time.time()
        
        if frame is None or frame.size == 0:
            return {
                "detections": [],
                "threat_count": 0,
                "latency_ms": 0.0,
                "status": "Invalid Frame"
            }

        h, w = frame.shape[:2]
        raw_detections = self.detector.infer(frame)
        latency_ms = round((time.time() - t0) * 1000, 2)

        # Apply domain postprocessing & threat classification
        threats = filter_and_classify_detections(
            raw_detections=raw_detections,
            confidence_threshold=confidence_threshold,
            frame_width=w,
            frame_height=h
        )

        status_text = "Potential Threat Detected" if len(threats) > 0 else "No potential threat detected"

        return {
            "detections": threats,
            "threat_count": len(threats),
            "latency_ms": latency_ms,
            "status": status_text,
            "timestamp": time.time()
        }

# Global singleton instance for API usage
detection_service = ThreatDetectionService()
