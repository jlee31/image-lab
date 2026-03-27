from utils.cv_imports import cv
from ._base import _ensure_image_copy


def apply_pencil(image):
    new_image = _ensure_image_copy(image)
    gray = cv.cvtColor(new_image, cv.COLOR_BGR2GRAY)
    inverted = cv.bitwise_not(gray)
    blurred = cv.GaussianBlur(inverted, (21, 21), sigmaX=0, sigmaY=0)
    inverted_blur = cv.bitwise_not(blurred)
    sketch = cv.divide(gray, inverted_blur, scale=256)
    return cv.cvtColor(sketch, cv.COLOR_GRAY2BGR)
