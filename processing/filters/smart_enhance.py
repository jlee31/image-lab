import cv2 as cv
import numpy as np
from PIL import Image, ImageFilter
from ._base import _ensure_image_copy
from .contrast import adjust_contrast_with_factor
from .saturation import adjust_saturation_with_factor


def apply_smart_enhance(image):
    enhanced = _ensure_image_copy(image)
    enhanced = adjust_contrast_with_factor(enhanced, 1.1)
    enhanced = adjust_saturation_with_factor(enhanced, 1.05)
    enhanced_pil = Image.fromarray(cv.cvtColor(enhanced, cv.COLOR_BGR2RGB))
    enhanced_pil = enhanced_pil.filter(ImageFilter.SHARPEN)
    return cv.cvtColor(np.array(enhanced_pil), cv.COLOR_RGB2BGR)
