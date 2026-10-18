"""Model Evaluation and Benchmark Metrics Reporter.
Calculates mAP@0.5, mAP@0.5:0.95, Precision, Recall, and Inference Latency.
Run: python training/evaluate.py --weights models/trained/weapon_yolov8_best.pt
"""

import argparse
import logging
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("EvaluateModel")

def evaluate(weights_path: str, data_yaml: str = "data/dataset.yaml", imgsz: int = 640):
    logger.info(f"Evaluating weights '{weights_path}' on validation set '{data_yaml}'...")

    model = YOLO(weights_path)
    metrics = model.val(data=data_yaml, imgsz=imgsz, split="val")

    print("\n" + "="*50)
    print("       MODEL EVALUATION METRICS REPORT")
    print("="*50)
    print(f" mAP@0.5      : {metrics.box.map50 * 100:.2f}%")
    print(f" mAP@0.5:0.95 : {metrics.box.map * 100:.2f}%")
    print(f" Precision    : {metrics.box.mp * 100:.2f}%")
    print(f" Recall       : {metrics.box.mr * 100:.2f}%")
    print(f" Inference Time: {metrics.speed['inference']:.2f} ms per frame")
    print("="*50 + "\n")

    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Weapon Detection Model")
    parser.add_argument("--weights", type=str, default="yolov8n.pt", help="Path to model weights (.pt)")
    parser.add_argument("--data", type=str, default="data/dataset.yaml", help="Path to dataset.yaml")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    args = parser.parse_args()

    evaluate(args.weights, args.data, args.imgsz)
