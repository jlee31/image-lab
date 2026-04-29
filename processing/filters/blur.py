import cv2 as cv
import numpy as np
from PIL import Image, ImageFilter
from ._base import _ensure_image_copy


def apply_blur_with_radius(image, radius: float):
    new_image = _ensure_image_copy(image)
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    blurred = image_pil.filter(ImageFilter.GaussianBlur(radius=radius))
    return cv.cvtColor(np.array(blurred), cv.COLOR_RGB2BGR)
