import numpy as np

from processing.filters import (
    adjust_brightness_with_factor,
    adjust_contrast_with_factor,
    apply_blur_with_radius,
    apply_smart_enhance,
)


def _dummy_image(width=64, height=64):
    # simple gradient image
    img = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            img[y, x] = [x % 256, y % 256, (x + y) % 256]
    return img


def test_adjust_brightness_with_factor_keeps_shape():
    img = _dummy_image()
    out = adjust_brightness_with_factor(img, 1.2)
    assert out.shape == img.shape
    assert out.dtype == img.dtype


def test_adjust_contrast_with_factor_keeps_shape():
    img = _dummy_image()
    out = adjust_contrast_with_factor(img, 1.1)
    assert out.shape == img.shape
    assert out.dtype == img.dtype


def test_apply_blur_with_radius_keeps_shape():
    img = _dummy_image()
    out = apply_blur_with_radius(img, 2)
    assert out.shape == img.shape
    assert out.dtype == img.dtype


def test_apply_smart_enhance_keeps_shape():
    img = _dummy_image()
    out = apply_smart_enhance(img)
    assert out.shape[:2] == img.shape[:2]

