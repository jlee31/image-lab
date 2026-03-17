from utils.imports import cv, os, messagebox
from processing.filters import apply_retro_filter, apply_sharpen, apply_blur_with_radius


def _iter_image_files(folder_path: str):
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"}
    for root, _, files in os.walk(folder_path):
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext in valid_exts:
                yield os.path.join(root, name)


def process_folder_basic(input_folder: str, output_folder: str, apply_retro: bool, apply_sharpen_flag: bool, blur_radius: float | None = None):
    """
    Apply a simple pipeline (retro / sharpen / blur) to all images in a folder.
    """
    if not os.path.isdir(input_folder):
        messagebox.showerror("Error", "Input folder does not exist.")
        return
    os.makedirs(output_folder, exist_ok=True)

    for path in _iter_image_files(input_folder):
        img = cv.imread(path)
        if img is None:
            continue
        result = img
        if apply_retro:
            result = apply_retro_filter(result)
        if apply_sharpen_flag:
            result = apply_sharpen(result)
        if blur_radius is not None and blur_radius > 0:
            result = apply_blur_with_radius(result, blur_radius)

        rel = os.path.relpath(path, input_folder)
        out_path = os.path.join(output_folder, rel)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        cv.imwrite(out_path, result)

