from utils.cv_imports import cv, np, Image, ImageEnhance
from ._base import _ensure_image_copy


def adjust_contrast_with_factor(image, factor: float):
    new_image = _ensure_image_copy(image)
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    enhanced = ImageEnhance.Contrast(image_pil).enhance(factor)
    return cv.cvtColor(np.array(enhanced), cv.COLOR_RGB2BGR)
