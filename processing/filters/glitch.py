from utils.cv_imports import np
from ._base import _ensure_image_copy


def apply_glitch(image, intensity: int = 10):
    new_image = _ensure_image_copy(image)
    height, width, _ = new_image.shape
    for _ in range(intensity):
        offset = np.random.randint(-10, 11, size=3)
        slice_h = np.random.randint(height // 20, height // 5)
        start_row = np.random.randint(0, height - slice_h)
        new_image[start_row:start_row + slice_h] = np.roll(
            new_image[start_row:start_row + slice_h], offset, axis=1
        )
    return new_image
