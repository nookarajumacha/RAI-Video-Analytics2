"""Offline Video File Threat Detection and Evaluation.
Run: python detection/video_detection.py --input test_video.mp4 --output output_annotated.mp4
"""

import sys
import os
import argparse
import cv2
import yaml
import time
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detection.detector import ThreatDetector
from alerts.visual import VisualHUD

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("VideoDetection")

def process_video(video_path: str, output_path: str = None, config_path: str = "config/config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    detector = ThreatDetector(config)
    hud = VisualHUD(show_hud=True, flash_on_threat=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    writer = None
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    prev_time = time.time()
    logger.info("Processing video stream...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        now = time.time()
        curr_fps = 1.0 / (now - prev_time) if (now - prev_time) > 0 else 30.0
        prev_time = now

        detections = detector.detect(frame)
        annotated = hud.draw_hud(frame, detections, fps=curr_fps)

        if writer:
            writer.write(annotated)
        else:
            cv2.imshow("Video Threat Detection (Press 'q' to stop)", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    if writer:
        writer.release()
        logger.info(f"Annotated video saved successfully to {output_path}")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Video with Threat Detector")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input video file path")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output annotated video path")
    parser.add_argument("--config", "-c", type=str, default="config/config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    process_video(args.input, args.output, args.config)
