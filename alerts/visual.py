"""Visual HUD and threat overlay rendering using OpenCV.
"""

import cv2
import numpy as np
from typing import List, Dict, Any

class VisualHUD:
    def __init__(self, show_hud: bool = True, flash_on_threat: bool = True):
        self.show_hud = show_hud
        self.flash_on_threat = flash_on_threat

    def draw_hud(self, frame: np.ndarray, detections: List[Dict[str, Any]], fps: float = 0.0) -> np.ndarray:
        """Render HUD overlays, bounding boxes, labels, and danger indicators on frame."""
        h, w = frame.shape[:2]
        annotated_frame = frame.copy()

        has_threat = any(d.get("is_threat", False) for d in detections)

        # 1. Threat warning perimeter border if threat detected
        if has_threat and self.flash_on_threat:
            cv2.rectangle(annotated_frame, (0, 0), (w, h), (0, 0, 255), 8)
            # Top Banner Alert
            cv2.rectangle(annotated_frame, (0, 0), (w, 50), (0, 0, 200), -1)
            cv2.putText(
                annotated_frame,
                "*** THREAT DETECTED - VERIFY IMMEDIATELY ***",
                (w // 2 - 270, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        # 2. Render Detections
        for det in detections:
            bbox = det["bbox"] # [x1, y1, x2, y2]
            label = det["label"]
            conf = det["confidence"]
            is_threat = det.get("is_threat", False)

            x1, y1, x2, y2 = map(int, bbox)
            box_color = (0, 0, 255) if is_threat else (0, 255, 0)

            # Draw target bounding box with corner brackets
            self._draw_corner_box(annotated_frame, (x1, y1, x2, y2), box_color)

            # Draw Label Tag
            caption = f"{label.upper()} {conf * 100:.1f}%"
            (tw, th), _ = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated_frame, (x1, max(0, y1 - 25)), (x1 + tw + 10, max(25, y1)), box_color, -1)
            cv2.putText(
                annotated_frame,
                caption,
                (x1 + 5, max(18, y1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        # 3. HUD Status Overlay
        if self.show_hud:
            # Bottom Status Bar
            cv2.rectangle(annotated_frame, (0, h - 35), (w, h), (20, 20, 20), -1)
            status_text = f"FPS: {fps:.1f} | SENSORS: ONLINE | TARGETS: WEAPONS (GUN/KNIFE)"
            cv2.putText(
                annotated_frame,
                status_text,
                (15, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0) if not has_threat else (0, 165, 255),
                1,
                cv2.LINE_AA,
            )

        return annotated_frame

    def _draw_corner_box(self, img: np.ndarray, pt: tuple, color: tuple, length: int = 15, thickness: int = 2):
        x1, y1, x2, y2 = pt
        # Main enclosing rectangle (semi-thin)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 1)

        # Corner brackets (thicker for tactical HUD aesthetic)
        t = thickness
        # Top-left
        cv2.line(img, (x1, y1), (x1 + length, y1), color, t)
        cv2.line(img, (x1, y1), (x1, y1 + length), color, t)
        # Top-right
        cv2.line(img, (x2, y1), (x2 - length, y1), color, t)
        cv2.line(img, (x2, y1), (x2, y1 + length), color, t)
        # Bottom-left
        cv2.line(img, (x1, y2), (x1 + length, y2), color, t)
        cv2.line(img, (x1, y2), (x1, y2 - length), color, t)
        # Bottom-right
        cv2.line(img, (x2, y2), (x2 - length, y2), color, t)
        cv2.line(img, (x2, y2), (x2, y2 - length), color, t)
