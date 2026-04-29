import cv2 as cv
import numpy as np
from ._base import _ensure_image_copy


def apply_vignette(image, intensity: float = 0.5):
    new_image = _ensure_image_copy(image)
    rows, cols = new_image.shape[:2]
    kernel_x = cv.getGaussianKernel(cols, cols / 2)
    kernel_y = cv.getGaussianKernel(rows, rows / 2)
    mask = kernel_y * kernel_x.T
    mask = mask / mask.max()
    mask = 1.0 - intensity * (1.0 - mask)
    new_image = new_image * mask[:, :, np.newaxis]
    return np.clip(new_image, 0, 255).astype(np.uint8)
