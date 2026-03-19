from utils.cv_imports import np
from utils.utils import check_image_loaded
from utils.customMessageBox import ctk_get_value


def apply_glitch(image):
    """Prompt for a glitch intensity and apply random horizontal channel shifts."""
    if not check_image_loaded(image):
        return
    new_image = image.copy()
    intensity = ctk_get_value(
        input="Enter Glitch Intensity (1 - 50)",
        minvalue=1, maxvalue=50, type=int,
    )
    if not intensity:
        return new_image
    height, width, _ = new_image.shape
    for _ in range(intensity):
        offset = np.random.randint(-10, 11, size=3)
        slice_h = np.random.randint(height // 20, height // 5)
        start_row = np.random.randint(0, height - slice_h)
        new_image[start_row:start_row + slice_h] = np.roll(
            new_image[start_row:start_row + slice_h], offset, axis=1
        )
    return new_image
