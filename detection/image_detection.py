"""Batch and Single Image Threat Detection Testing.
Run: python detection/image_detection.py --input path/to/image.jpg
"""

import sys
import os
import argparse
import cv2
import yaml
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detection.detector import ThreatDetector
from alerts.visual import VisualHUD

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ImageDetection")

def test_image(image_path: str, output_path: str = None, config_path: str = "config/config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    detector = ThreatDetector(config)
    hud = VisualHUD(show_hud=True, flash_on_threat=True)

    if not os.path.exists(image_path):
        logger.error(f"Image not found at {image_path}")
        return

    frame = cv2.imread(image_path)
    if frame is None:
        logger.error(f"Failed to read image at {image_path}")
        return

    logger.info(f"Running detection on {image_path}...")
    detections = detector.detect(frame)

    logger.info(f"Detected {len(detections)} objects:")
    for d in detections:
        logger.info(f"  - [{d['label']}] Confidence: {d['confidence']*100:.1f}%, Threat: {d['is_threat']}")

    annotated = hud.draw_hud(frame, detections, fps=0.0)

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cv2.imwrite(output_path, annotated)
        logger.info(f"Saved annotated result to {output_path}")
    else:
        cv2.imshow("Detection Result (Press any key to close)", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Threat Detector on Static Images")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input image or directory")
    parser.add_argument("--output", "-o", type=str, default=None, help="Path to save annotated output image")
    parser.add_argument("--config", "-c", type=str, default="config/config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    test_image(args.input, args.output, args.config)
