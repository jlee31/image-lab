from utils.cv_imports import cv, np, Image, ImageEnhance
from utils.utils import check_image_loaded


def apply_retro_filter(image):
    """Boost reds, reduce blues, and lift contrast to create a retro look."""
    if not check_image_loaded(image):
        return
    new_image = image.copy()
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    r, g, b = image_pil.split()
    r = r.point(lambda i: i * 1.3)
    b = b.point(lambda i: i * 0.8)
    image_pil = Image.merge("RGB", (r, g, b))
    image_pil = ImageEnhance.Contrast(image_pil).enhance(1.2)
    return cv.cvtColor(np.array(image_pil), cv.COLOR_RGB2BGR)
