import cv2 as cv
import numpy as np
from ._base import _ensure_image_copy


def apply_noise_with_intensity(image, intensity: float):
    new_image = _ensure_image_copy(image)
    clamped = max(0.0, min(intensity, 1.0))
    max_noise = int(max(1, clamped * 50))
    noise = np.random.randint(0, max_noise + 1, new_image.shape, dtype=np.uint8)
    return cv.add(new_image, noise)
