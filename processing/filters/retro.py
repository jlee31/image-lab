import cv2 as cv
import numpy as np
from PIL import Image, ImageEnhance
from ._base import _ensure_image_copy


def apply_retro_filter(image):
    new_image = _ensure_image_copy(image)
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    r, g, b = image_pil.split()
    r = r.point(lambda i: i * 1.3)
    b = b.point(lambda i: i * 0.8)
    image_pil = Image.merge("RGB", (r, g, b))
    image_pil = ImageEnhance.Contrast(image_pil).enhance(1.2)
    return cv.cvtColor(np.array(image_pil), cv.COLOR_RGB2BGR)
