from .imports import *

def load_image_via_dialog():
    image = filedialog.askopenfilename(
        filetypes=[
            ("JPEG files", "*.jpg;*.jpeg"),
            ("PNG files", "*.png"),
            ("GIF files", "*.gif"),
            ("All files", "*.*")
        ])
    if image:
        return image
    else:
        messagebox.ERROR("Error", "Please pick a valid image")
        return 
    
def save_image_via_dialog(image):
    if image is None:
        messagebox.showerror("Error", "Please select an Image first")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("BMP files", "*.bmp")])
    if file_path:
        cv.imwrite(filename=file_path, img=image)
        messagebox.showinfo("Success", "Image Saved Successfully")

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
