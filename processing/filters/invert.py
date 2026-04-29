import cv2 as cv
from ._base import _ensure_image_copy


def apply_invert(image):
    return cv.bitwise_not(_ensure_image_copy(image))
