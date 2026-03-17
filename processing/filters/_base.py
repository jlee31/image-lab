from utils.utils import check_image_loaded


def _ensure_image_copy(image):
    """Return a mutable copy of the image, or None if no image is loaded."""
    if not check_image_loaded(image):
        return None
    return image.copy()
