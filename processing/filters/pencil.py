from utils.imports import cv
from utils.utils import check_image_loaded


def apply_pencil(image):
    """Convert the image to a pencil-sketch look using divide blending."""
    if not check_image_loaded(image):
        return
    new_image = image.copy()
    gray = cv.cvtColor(new_image, cv.COLOR_BGR2GRAY)
    inverted = cv.bitwise_not(gray)
    blurred = cv.GaussianBlur(inverted, (21, 21), sigmaX=0, sigmaY=0)
    inverted_blur = cv.bitwise_not(blurred)
    sketch = cv.divide(gray, inverted_blur, scale=256)
    return cv.cvtColor(sketch, cv.COLOR_GRAY2BGR)
