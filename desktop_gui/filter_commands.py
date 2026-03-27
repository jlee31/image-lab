"""
desktop_gui/filter_commands.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dialog-based wrappers around the pure processing functions.
These belong in desktop_gui because they require a GUI (CTkInputDialog).
The API uses the pure _with_factor / _with_radius functions directly.
"""

from utils.customMessageBox import ctk_get_value
from utils.gui_utils import check_image_loaded
from processing.filters import (
    adjust_brightness_with_factor,
    adjust_contrast_with_factor,
    adjust_saturation_with_factor,
    apply_blur_with_radius,
    apply_noise_with_intensity,
    apply_glitch,
    apply_vignette,
    apply_pixels,
)


def adjust_brightness(image):
    if not check_image_loaded(image):
        return
    factor = ctk_get_value(
        input="Enter Brightness Factor (0.0 to 2.0)",
        minvalue=0.0, maxvalue=2.0, type=float,
    )
    if factor:
        return adjust_brightness_with_factor(image, factor)
    return image.copy()


def adjust_contrast(image):
    if not check_image_loaded(image):
        return
    factor = ctk_get_value(
        input="Enter Contrast Factor (0.0 to 2.0)",
        minvalue=0.0, maxvalue=2.0, type=float,
    )
    if factor:
        return adjust_contrast_with_factor(image, factor)
    return image.copy()


def adjust_saturation(image):
    if not check_image_loaded(image):
        return
    factor = ctk_get_value(
        input="Enter Saturation Factor (0.0 to 2.0)",
        minvalue=0.0, maxvalue=2.0, type=float,
    )
    if factor:
        return adjust_saturation_with_factor(image, factor)
    return image.copy()


def apply_blur(image):
    if not check_image_loaded(image):
        return
    radius = ctk_get_value(
        input="Enter Blur Radius (1 to 10)",
        minvalue=1, maxvalue=10, type=int,
    )
    if radius:
        return apply_blur_with_radius(image, radius)
    return image.copy()


def apply_noise(image):
    if not check_image_loaded(image):
        return
    intensity = ctk_get_value(
        input="Enter Noise Intensity (0.0 to 1.0)",
        minvalue=0.0, maxvalue=1.0, type=float,
    )
    if intensity is not None:
        return apply_noise_with_intensity(image, intensity)
    return image.copy()


def apply_glitch_dialog(image):
    if not check_image_loaded(image):
        return
    intensity = ctk_get_value(
        input="Enter Glitch Intensity (1 to 50)",
        minvalue=1, maxvalue=50, type=int,
    )
    if intensity:
        return apply_glitch(image, intensity)
    return image.copy()


def apply_vignette_dialog(image):
    if not check_image_loaded(image):
        return
    intensity = ctk_get_value(
        input="Enter Vignette Intensity (0.0 to 1.0)",
        minvalue=0.0, maxvalue=1.0, type=float,
    )
    if intensity:
        return apply_vignette(image, intensity)
    return image.copy()


def apply_pixels_dialog(image):
    if not check_image_loaded(image):
        return
    factor = ctk_get_value(
        input="Enter Pixel Factor (2 to 50)",
        minvalue=2, maxvalue=50, type=int,
    )
    if factor:
        return apply_pixels(image, factor)
    return image.copy()
