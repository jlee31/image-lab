from utils.imports import cv, np, Image, ImageFilter
from utils.utils import check_image_loaded


def apply_sharpen(image):
    """Apply a standard sharpening filter."""
    if not check_image_loaded(image):
        return
    new_image = image.copy()
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    sharpened = image_pil.filter(ImageFilter.SHARPEN)
    return cv.cvtColor(np.array(sharpened), cv.COLOR_RGB2BGR)
