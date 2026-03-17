from utils.imports import cv, np
from utils.utils import check_image_loaded
from utils.customMessageBox import ctk_get_value
from ._base import _ensure_image_copy


def apply_noise(image):
    """Prompt the user for a noise intensity and apply it."""
    if not check_image_loaded(image):
        return
    new_image = image.copy()
    intensity = ctk_get_value(
        input="Enter Noise Factor (From 0 to 1)",
        minvalue=0.0, maxvalue=1.0, type=float,
    )
    if intensity is not None:
        new_image = apply_noise_with_intensity(new_image, intensity)
    return new_image


def apply_noise_with_intensity(image, intensity: float):
    """Apply noise directly with a given intensity (used by sliders)."""
    new_image = _ensure_image_copy(image)
    if new_image is None:
        return image
    clamped = max(0.0, min(intensity, 1.0))
    max_noise = int(max(1, clamped * 50))
    noise = np.random.randint(0, max_noise + 1, new_image.shape, dtype=np.uint8)
    return cv.add(new_image, noise)
