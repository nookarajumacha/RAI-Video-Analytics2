"""Frame preprocessing functions for video input.
"""

import cv2
import numpy as np
from typing import Tuple

def preprocess_frame(frame: np.ndarray, target_size: int = 640) -> Tuple[np.ndarray, float, Tuple[int, int]]:
    """Resizes and letterboxes frame while preserving aspect ratio.
    Returns:
        (preprocessed_image, scale_factor, (pad_w, pad_h))
    """
    if frame is None or frame.size == 0:
        raise ValueError("Invalid or empty frame provided for preprocessing.")

    h, w = frame.shape[:2]
    scale = min(target_size / h, target_size / w)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    pad_w = (target_size - new_w) // 2
    pad_h = (target_size - new_h) // 2

    canvas = np.full((target_size, target_size, 3), 114, dtype=np.uint8)
    canvas[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = resized

    return canvas, scale, (pad_w, pad_h)
