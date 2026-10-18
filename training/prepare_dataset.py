"""Dataset Preparation Pipeline for Custom Weapon Detection Model.
Extracts and converts HuggingFace WeaponDetection_Grouped into YOLO format.
Classes:
  0: firearm (GUN)
  1: knife (KNIFE)
"""

import os
import glob
import logging
import pyarrow.parquet as pq

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("DatasetPrep")

def prepare_dataset(max_train_samples: int = 400, max_val_samples: int = 100):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(base_dir, "data", "processed")
    
    train_img_dir = os.path.join(processed_dir, "images", "train")
    val_img_dir = os.path.join(processed_dir, "images", "val")
    train_lbl_dir = os.path.join(processed_dir, "labels", "train")
    val_lbl_dir = os.path.join(processed_dir, "labels", "val")

    for d in [train_img_dir, val_img_dir, train_lbl_dir, val_lbl_dir]:
        os.makedirs(d, exist_ok=True)

    # Locate parquet dataset in cache
    parquet_files = glob.glob(
        os.path.expanduser("~/.cache/huggingface/hub/datasets--Subh775--WeaponDetection_Grouped/**/validation*.parquet"),
        recursive=True
    )
    if not parquet_files:
        raise FileNotFoundError("WeaponDetection_Grouped parquet not found in HuggingFace cache.")

    parquet_path = parquet_files[0]
    logger.info(f"Reading dataset from: {parquet_path}")
    table = pq.read_table(parquet_path)
    total_rows = len(table)
    logger.info(f"Total available samples: {total_rows}")

    def convert_and_save(row, img_dir, lbl_dir, prefix):
        img_id = row['image_id']
        img_bytes = row['image']['bytes']
        w = float(row['width'])
        h = float(row['height'])
        objects = row['objects']

        bboxes = objects['bbox']
        categories = objects['category']

        # Filter only GUN (0) and KNIFE (1)
        valid_labels = []
        for bbox, cat in zip(bboxes, categories):
            if cat in [0, 1]:
                # bbox is [x_min, y_min, box_w, box_h]
                x_min, y_min, box_w, box_h = bbox
                if box_w <= 0 or box_h <= 0 or w <= 0 or h <= 0:
                    continue
                
                # YOLO format: class_id, x_center, y_center, norm_w, norm_h
                x_center = (x_min + box_w / 2.0) / w
                y_center = (y_min + box_h / 2.0) / h
                norm_w = box_w / w
                norm_h = box_h / h

                # Clamp to 0..1
                x_center = max(0.0, min(1.0, x_center))
                y_center = max(0.0, min(1.0, y_center))
                norm_w = max(0.0, min(1.0, norm_w))
                norm_h = max(0.0, min(1.0, norm_h))

                valid_labels.append(f"{cat} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}")

        # Only save if image contains at least one weapon
        if not valid_labels:
            return False

        # Save Image
        img_filename = f"{prefix}_{img_id}.jpg"
        img_path = os.path.join(img_dir, img_filename)
        with open(img_path, "wb") as f_img:
            f_img.write(img_bytes)

        # Save Label
        lbl_filename = f"{prefix}_{img_id}.txt"
        lbl_path = os.path.join(lbl_dir, lbl_filename)
        with open(lbl_path, "w") as f_lbl:
            f_lbl.write("\n".join(valid_labels) + "\n")

        return True

    train_saved = 0
    val_saved = 0

    rows_data = table.to_pylist()
    for row in rows_data:
        if train_saved < max_train_samples:
            if convert_and_save(row, train_img_dir, train_lbl_dir, "train"):
                train_saved += 1
        elif val_saved < max_val_samples:
            if convert_and_save(row, val_img_dir, val_lbl_dir, "val"):
                val_saved += 1
        else:
            break

    logger.info(f"Dataset successfully prepared: {train_saved} training images, {val_saved} validation images.")

    # Write YOLO dataset.yaml with absolute paths
    abs_processed = os.path.abspath(processed_dir).replace("\\", "/")
    yaml_content = f"""# Custom YOLO Weapon Detection Dataset
path: {abs_processed}
train: images/train
val: images/val

# Classes:
# 0: firearm
# 1: knife
nc: 2
names:
  0: firearm
  1: knife
"""

    yaml_path = os.path.join(base_dir, "data", "dataset.yaml")
    with open(yaml_path, "w") as f_yaml:
        f_yaml.write(yaml_content)

    logger.info(f"Updated dataset YAML definition at: {yaml_path}")
    return train_saved, val_saved

if __name__ == "__main__":
    prepare_dataset()
