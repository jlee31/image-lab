from utils.imports import cv, np, Image, ImageFilter
from utils.utils import check_image_loaded
from utils.customMessageBox import ctk_get_value
from ._base import _ensure_image_copy


def apply_blur(image):
    """Prompt the user for a blur radius and apply Gaussian blur."""
    if not check_image_loaded(image):
        return
    new_image = image.copy()
    radius = ctk_get_value(
        input="Enter Blur Factor (1 to 10)",
        minvalue=1, maxvalue=10, type=int,
    )
    if radius:
        new_image = apply_blur_with_radius(new_image, radius)
    return new_image


def apply_blur_with_radius(image, radius: float):
    """Apply Gaussian blur directly with a given radius (used by sliders)."""
    new_image = _ensure_image_copy(image)
    if new_image is None:
        return image
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    blurred = image_pil.filter(ImageFilter.GaussianBlur(radius=radius))
    return cv.cvtColor(np.array(blurred), cv.COLOR_RGB2BGR)
