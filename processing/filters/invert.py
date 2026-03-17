from utils.imports import cv
from utils.utils import check_image_loaded


def apply_invert(image):
    """Invert all pixel values (bitwise NOT)."""
    if not check_image_loaded(image):
        return
    return cv.bitwise_not(image.copy())
