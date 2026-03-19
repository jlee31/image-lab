from utils.cv_imports import cv
from utils.utils import check_image_loaded
from utils.customMessageBox import ctk_get_value


def apply_pixels(image):
    """Prompt for a pixel block size and apply a pixelation effect."""
    if not check_image_loaded(image):
        return
    new_image = image.copy()
    factor = ctk_get_value(
        input="Enter Pixel Factor (From 2 to 50)",
        minvalue=2, maxvalue=50, type=int,
    )
    if factor:
        height, width = new_image.shape[:2]
        small = cv.resize(
            new_image, (width // factor, height // factor),
            interpolation=cv.INTER_LINEAR,
        )
        new_image = cv.resize(small, (width, height), interpolation=cv.INTER_NEAREST)
    return new_image
