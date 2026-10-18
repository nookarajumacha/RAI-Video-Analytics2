"""Post-processing and threat classification utilities.
"""

from typing import List, Dict, Any
from backend.config.settings import settings

def filter_and_classify_detections(
    raw_detections: List[Dict[str, Any]],
    confidence_threshold: float,
    frame_width: int,
    frame_height: int
) -> List[Dict[str, Any]]:
    """Applies strict confidence filtering, size checks, and threat classification.
    Every threat is explicitly flagged as a Potential Threat requiring human verification.
    """
    total_area = float(frame_width * frame_height) if (frame_width > 0 and frame_height > 0) else 1.0
    processed_threats = []

    for det in raw_detections:
        cls_name = det.get("class_name", "").lower()
        conf = float(det.get("confidence", 0.0))
        bbox = det.get("bbox", [0, 0, 0, 0])

        if conf < confidence_threshold:
            continue

        # Area filtering: Reject noise < 0.2% or whole-screen glitches > 85%
        x1, y1, x2, y2 = bbox
        box_w = max(0, x2 - x1)
        box_h = max(0, y2 - y1)
        box_area = box_w * box_h
        area_ratio = box_area / total_area

        if area_ratio < 0.002 or area_ratio > 0.85:
            continue

        # Check if class matches predefined threat target
        is_threat = False
        standard_label = cls_name.title()

        if cls_name in ["gun", "firearm", "pistol", "rifle"]:
            is_threat = True
            standard_label = "Firearm"
        elif cls_name in ["knife", "blade", "dagger"]:
            is_threat = True
            standard_label = "Knife"
        elif any(target in cls_name for target in settings.TARGET_THREAT_CLASSES):
            is_threat = True
            standard_label = cls_name.title()

        if is_threat:
            processed_threats.append({
                "object_type": standard_label.lower(),
                "label": standard_label,
                "confidence": conf,
                "bbox": [round(coord, 2) for coord in bbox],
                "area_ratio": round(area_ratio, 4),
                "is_threat": True,
                "status": "Potential Threat",
                "action": "Human verification required"
            })

    return processed_threats
