from .imports import *
import platform
import os 

def load_image_via_dialog():
    # Check if we're on macOS and use a more compatible approach
    if platform.system() == "Darwin":
        return _load_image_macos()
    else:
        return _load_image_generic()

def _load_image_macos():
    """macOS-specific image loading with better compatibility"""
    try:
        # Use a very simple file dialog first
        file_path = filedialog.askopenfilename(
            title="Select Image File"
        )
        if file_path:
            # Validate file extension manually
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in valid_extensions:
                return file_path
            else:
                messagebox.showerror("Error", f"Unsupported file type: {file_ext}")
                return None
        return None
    except Exception as e:
        print(f"macOS file dialog error: {e}")
        return None

def _load_image_generic():
    """Generic image loading for other platforms"""
    try:
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*")
            ])
        return file_path if file_path else None
    except Exception as e:
        print(f"Generic file dialog error: {e}")
        return None

def save_image_via_dialog(image):
    if platform.system() == "Darwin":
        return _save_image_macos(image)
    else:
        return _save_image_generic(image)

def _save_image_macos(image):
    """macOS-specific image saving"""
    try:
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png"
        )
        if file_path:
            cv.imwrite(filename=file_path, img=image)
            messagebox.showinfo("Success", "Image Saved Successfully")
    except Exception as e:
        print(f"macOS save dialog error: {e}")
        messagebox.showerror("Error", "Failed to save image")

def _save_image_generic(image):
    """Generic image saving for other platforms"""
    try:
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*")
            ])
        if file_path:
            cv.imwrite(filename=file_path, img=image)
            messagebox.showinfo("Success", "Image Saved Successfully")
    except Exception as e:
        print(f"Generic save dialog error: {e}")
        messagebox.showerror("Error", "Failed to save image")

def push_undo(undo_stack, redo_stack, current_image, max_stack_size=20):
    undo_stack.append(current_image.copy())
    if len(undo_stack) > max_stack_size:
        undo_stack.pop(0)
    redo_stack.clear()

def undo(undo_stack, redo_stack, current_image):
    if undo_stack:
        redo_stack.append(current_image.copy())
        return undo_stack.pop()
    return current_image  

def redo(undo_stack, redo_stack, current_image):
    if redo_stack:
        undo_stack.append(current_image.copy())
        return redo_stack.pop()
    return current_image  

def check_image_loaded(image):
    if image is None:
        messagebox.showerror("Error", "No image loaded.")
        return False
    return True
