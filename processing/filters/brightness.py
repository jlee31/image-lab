from utils.cv_imports import cv, np, Image, ImageEnhance
from utils.utils import check_image_loaded
from utils.customMessageBox import ctk_get_value
from ._base import _ensure_image_copy


def adjust_brightness(image):
    """Prompt the user for a brightness factor and apply it."""
    if not check_image_loaded(image):
        return
    new_image = image.copy()
    factor = ctk_get_value(
        input="Enter Brightness Factor (0.0 to 2.0)",
        minvalue=0.0, maxvalue=2.0, type=float,
    )
    if factor:
        image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
        enhanced = ImageEnhance.Brightness(image_pil).enhance(factor)
        new_image = cv.cvtColor(np.array(enhanced), cv.COLOR_RGB2BGR)
    return new_image


def adjust_brightness_with_factor(image, factor: float):
    """Apply brightness directly with a given factor (used by sliders)."""
    new_image = _ensure_image_copy(image)
    if new_image is None:
        return image
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    enhanced = ImageEnhance.Brightness(image_pil).enhance(factor)
    return cv.cvtColor(np.array(enhanced), cv.COLOR_RGB2BGR)
