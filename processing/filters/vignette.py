from utils.imports import cv, np
from utils.utils import check_image_loaded
from utils.customMessageBox import ctk_get_value


def apply_vignette(image):
    """Prompt the user for a vignette intensity and apply a Gaussian vignette mask."""
    if not check_image_loaded(image):
        return
    new_image = image.copy()
    intensity = ctk_get_value(
        input="Enter Vignette Intensity (0.0 to 1.0)",
        minvalue=0.0, maxvalue=1.0, type=float,
    )
    if intensity:
        rows, cols = new_image.shape[:2]
        kernel_x = cv.getGaussianKernel(cols, cols / 2)
        kernel_y = cv.getGaussianKernel(rows, rows / 2)
        mask = kernel_y * kernel_x.T
        mask = 255 * mask / (1 - intensity)
        mask = mask * intensity + (1 - intensity)
        new_image = new_image * mask[:, :, np.newaxis]
        new_image = np.clip(new_image, 0, 255).astype(np.uint8)
    return new_image
