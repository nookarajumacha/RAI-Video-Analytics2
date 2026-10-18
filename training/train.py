"""Model Training Script for Custom Firearm & Knife Detection.
Run: python training/train.py --epochs 50 --imgsz 640 --batch 16
"""

import os
import argparse
import logging
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TrainPipeline")

def train_model(
    data_yaml: str = "data/dataset.yaml",
    base_model: str = "yolov8n.pt",
    epochs: int = 50,
    imgsz: int = 640,
    batch_size: int = 16,
    project_dir: str = "runs/train",
    name: str = "weapon_detector_v1"
):
    logger.info("Initializing Ultralytics YOLO training pipeline...")
    logger.info(f"Dataset config: {data_yaml}")
    logger.info(f"Base model: {base_model} | Epochs: {epochs} | Batch: {batch_size}")

    if not os.path.exists(data_yaml):
        raise FileNotFoundError(f"Dataset YAML definition not found at: {data_yaml}")

    # Load baseline model
    model = YOLO(base_model)

    device = "0" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
    # Train model
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch_size,
        project=project_dir,
        name=name,
        patience=15,
        save=True,
        device=device
    )


    logger.info("Training complete!")
    save_dir = getattr(results, "save_dir", None)
    best_weights = None
    if save_dir:
        cand = os.path.join(str(save_dir), "weights", "best.pt")
        if os.path.exists(cand):
            best_weights = cand

    if not best_weights:
        # Search runs directory for newest best.pt
        import glob
        matches = glob.glob("runs/**/best.pt", recursive=True)
        if matches:
            best_weights = max(matches, key=os.path.getmtime)

    if best_weights and os.path.exists(best_weights):
        os.makedirs("models/trained", exist_ok=True)
        import shutil
        dest1 = "models/trained/weapon_threat_yolov8.pt"
        dest2 = "models/trained/weapon_yolov8_custom_best.pt"
        shutil.copy(best_weights, dest1)
        shutil.copy(best_weights, dest2)
        logger.info(f"Successfully exported new trained model weights to: {dest1} & {dest2}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Custom Weapon Detection Model")
    parser.add_argument("--data", type=str, default="data/dataset.yaml", help="Path to dataset.yaml")
    parser.add_argument("--base", type=str, default="yolov8n.pt", help="Base model weights (yolov8n.pt, yolov8s.pt)")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Input image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--name", type=str, default="weapon_detector_v1", help="Run name")
    args = parser.parse_args()

    train_model(
        data_yaml=args.data,
        base_model=args.base,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch_size=args.batch,
        name=args.name
    )
