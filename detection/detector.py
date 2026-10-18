"""High-Accuracy YOLO Threat Detection Engine with Temporal Confirmation & ByteTrack Tracking.
Specially tuned for firearm & knife identification with false-positive suppression.
"""

import os
import logging
from typing import List, Dict, Any
from collections import defaultdict

logger = logging.getLogger("ThreatDetector")

class ThreatDetector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("model", {})
        self.weights_path = self.config.get("weights", "models/trained/weapon_threat_yolov8.pt")
        self.conf_threshold = self.config.get("confidence_threshold", 0.50)
        self.iou_threshold = self.config.get("iou_threshold", 0.45)
        self.img_size = self.config.get("img_size", 640)
        self.device = self.config.get("device", "auto")
        self.enable_tracking = self.config.get("enable_tracking", True)
        
        # Temporal consistency & false positive suppression parameters
        self.min_consecutive_frames = self.config.get("temporal_confirmation_frames", 2)
        self.min_box_area_ratio = self.config.get("min_box_area_ratio", 0.003)
        self.max_box_area_ratio = self.config.get("max_box_area_ratio", 0.85)

        # Track history for temporal confirmation: {track_id or spatial_key: hit_count}
        self._threat_hits = defaultdict(int)
        self._frame_counter = 0

        # Build threat dictionary
        self.threat_classes = {}
        for tc in self.config.get("threat_classes", []):
            name = tc["name"].lower()
            self.threat_classes[name] = {
                "display_name": tc.get("display_name", name.title()),
                "alert_priority": tc.get("alert_priority", "HIGH"),
                "min_confidence": tc.get("min_confidence", self.conf_threshold)
            }

        self.model = None
        self._load_model()

    def _load_model(self):
        """Loads Ultralytics YOLO model."""
        try:
            from ultralytics import YOLO

            # Prefer specialized trained threat model if present
            if not os.path.exists(self.weights_path):
                alt_weights = "models/pretrained/yolov8n.pt"
                if os.path.exists(alt_weights):
                    self.weights_path = alt_weights
                else:
                    self.weights_path = "yolov8n.pt"
                logger.warning(f"Target weights not found. Defaulting to: {self.weights_path}")

            logger.info(f"Loading High-Accuracy YOLO weights from: {self.weights_path}")
            self.model = YOLO(self.weights_path)
            logger.info(f"YOLO model ready with classes: {self.model.names}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None

    def detect(self, frame) -> List[Dict[str, Any]]:
        """Run object detection with ByteTrack tracking and multi-frame temporal confirmation."""
        if self.model is None or frame is None:
            return []

        h, w = frame.shape[:2]
        total_frame_area = float(w * h)
        self._frame_counter += 1

        try:
            # Run inference (use track if enabled for smoother multi-frame persistence)
            if self.enable_tracking:
                results = self.model.track(
                    source=frame,
                    conf=self.conf_threshold,
                    iou=self.iou_threshold,
                    imgsz=self.img_size,
                    persist=True,
                    tracker="bytetrack.yaml",
                    verbose=False
                )
            else:
                results = self.model.predict(
                    source=frame,
                    conf=self.conf_threshold,
                    iou=self.iou_threshold,
                    imgsz=self.img_size,
                    verbose=False
                )
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return []

        detections = []
        if not results:
            return detections

        r = results[0]
        boxes = r.boxes
        if boxes is None or len(boxes) == 0:
            # Decay hit counters on clean frames
            if self._frame_counter % 5 == 0:
                self._decay_hits()
            return detections

        for box in boxes:
            cls_id = int(box.cls[0].item())
            class_name = self.model.names[cls_id].lower()
            confidence = float(box.conf[0].item())
            xyxy = box.xyxy[0].tolist() # [x1, y1, x2, y2]
            
            # Track ID if available from ByteTrack
            track_id = int(box.id[0].item()) if (box.id is not None) else None

            # Calculate box area ratio to eliminate spurious pixel noise or full-frame blobs
            box_w = max(0, xyxy[2] - xyxy[0])
            box_h = max(0, xyxy[3] - xyxy[1])
            box_area = box_w * box_h
            area_ratio = box_area / total_frame_area

            if area_ratio < self.min_box_area_ratio or area_ratio > self.max_box_area_ratio:
                continue # Reject unrealistic box dimension

            # Determine if this detection is a targeted threat
            is_potential_threat = False
            display_name = class_name.title()

            if class_name in self.threat_classes:
                threat_info = self.threat_classes[class_name]
                if confidence >= threat_info["min_confidence"]:
                    is_potential_threat = True
                    display_name = threat_info["display_name"]
            elif class_name in ["gun", "pistol", "rifle", "firearm", "knife", "blade", "dagger", "grenade"]:
                if confidence >= self.conf_threshold:
                    is_potential_threat = True
                    display_name = f"Threat ({class_name.title()})"

            # Temporal Confirmation Gate (Anti-Flicker Filter)
            # Confirms the threat across consecutive frames before raising alert
            is_confirmed_threat = False
            if is_potential_threat:
                spatial_key = track_id if track_id is not None else (int(xyxy[0]//50), int(xyxy[1]//50), class_name)
                self._threat_hits[spatial_key] += 1
                hit_count = self._threat_hits[spatial_key]

                if hit_count >= self.min_consecutive_frames or confidence >= 0.75:
                    is_confirmed_threat = True
            else:
                if track_id is not None and track_id in self._threat_hits:
                    self._threat_hits[track_id] = max(0, self._threat_hits[track_id] - 1)

            detections.append({
                "class_id": cls_id,
                "label": display_name,
                "raw_class": class_name,
                "confidence": confidence,
                "bbox": xyxy,
                "track_id": track_id,
                "is_threat": is_confirmed_threat
            })

        return detections

    def _decay_hits(self):
        """Gradually decrements stale threat counters."""
        for k in list(self._threat_hits.keys()):
            self._threat_hits[k] -= 1
            if self._threat_hits[k] <= 0:
                del self._threat_hits[k]
