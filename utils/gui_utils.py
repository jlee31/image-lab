import platform
import os
import cv2 as cv
from utils.gui_imports import filedialog, messagebox


def check_image_loaded(image, error_dialogs_enabled=None):
    if image is None:
        if error_dialogs_enabled is None or error_dialogs_enabled.get():
            messagebox.showerror("Error", "No image loaded.")
        return False
    return True


def load_image_via_dialog():
    if platform.system() == "Darwin":
        return _load_image_macos()
    else:
        return _load_image_generic()


def _load_image_macos():
    try:
        file_path = filedialog.askopenfilename(title="Select Image File")
        if file_path:
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
            if os.path.splitext(file_path)[1].lower() in valid_extensions:
                return file_path
            else:
                messagebox.showerror("Error", f"Unsupported file type")
        return None
    except Exception as e:
        print(f"macOS file dialog error: {e}")
        return None


def _load_image_generic():
    try:
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("All files", "*")
            ])
        return file_path if file_path else None
    except Exception as e:
        print(f"File dialog error: {e}")
        return None


def save_image_via_dialog(image, success_popups_enabled=None, error_dialogs_enabled=None):
    if platform.system() == "Darwin":
        return _save_image_macos(image, success_popups_enabled, error_dialogs_enabled)
    else:
        return _save_image_generic(image, success_popups_enabled, error_dialogs_enabled)


def _save_image_macos(image, success_popups_enabled=None, error_dialogs_enabled=None):
    try:
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png"
        )
        if file_path:
            cv.imwrite(filename=file_path, img=image)
            if success_popups_enabled is None or success_popups_enabled.get():
                messagebox.showinfo("Success", "Image Saved Successfully")
    except Exception as e:
        print(f"Save dialog error: {e}")
        if error_dialogs_enabled is None or error_dialogs_enabled.get():
            messagebox.showerror("Error", "Failed to save image")


def _save_image_generic(image, success_popups_enabled=None, error_dialogs_enabled=None):
    try:
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*")]
        )
        if file_path:
            cv.imwrite(filename=file_path, img=image)
            if success_popups_enabled is None or success_popups_enabled.get():
                messagebox.showinfo("Success", "Image Saved Successfully")
    except Exception as e:
        print(f"Save dialog error: {e}")
        if error_dialogs_enabled is None or error_dialogs_enabled.get():
            messagebox.showerror("Error", "Failed to save image")
