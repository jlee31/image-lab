from utils.imports import cv, np, Image, ImageFilter
from utils.utils import check_image_loaded
from .contrast import adjust_contrast_with_factor
from .saturation import adjust_saturation_with_factor


def apply_smart_enhance(image):
    """
    Preset enhancement: gentle contrast + saturation boost, then light sharpening.
    Based on human-tuned values for a natural-looking result.
    """
    if not check_image_loaded(image):
        return
    enhanced = image.copy()
    enhanced = adjust_contrast_with_factor(enhanced, 1.1)
    enhanced = adjust_saturation_with_factor(enhanced, 1.05)
    enhanced_pil = Image.fromarray(cv.cvtColor(enhanced, cv.COLOR_BGR2RGB))
    enhanced_pil = enhanced_pil.filter(ImageFilter.SHARPEN)
    return cv.cvtColor(np.array(enhanced_pil), cv.COLOR_RGB2BGR)
