import cv2 as cv
from ._base import _ensure_image_copy


def apply_pixels(image, factor: int = 10):
    new_image = _ensure_image_copy(image)
    height, width = new_image.shape[:2]
    small = cv.resize(
        new_image, (width // factor, height // factor),
        interpolation=cv.INTER_LINEAR,
    )
    return cv.resize(small, (width, height), interpolation=cv.INTER_NEAREST)
