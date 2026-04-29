import cv2 as cv
import numpy as np
from PIL import Image, ImageFilter
from ._base import _ensure_image_copy


def apply_sharpen(image):
    new_image = _ensure_image_copy(image)
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    sharpened = image_pil.filter(ImageFilter.SHARPEN)
    return cv.cvtColor(np.array(sharpened), cv.COLOR_RGB2BGR)
