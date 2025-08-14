'''
This file is responsible for:
Creating the Tkinter window and widgets (buttons, labels, canvas, etc.).
Handling user interactions (button clicks, sliders, etc.).
Displaying images (e.g., showing OpenCV processed images in the GUI).
Calling image processing functions when needed.
Managing the app’s main event loop.
'''

from utils.imports import * 
from utils.utils import *
from processing.image_filters import *
from utils.customMessageBox import ctk_messagebox

class AppWindow:
    # * Initial Setup
    def __init__(self):
        ctk.set_appearance_mode("System")  # Optional: light/dark mode
        ctk.set_default_color_theme("blue")  # Optional: theme color

        self.app = ctk.CTk()
        self.app.title("Image Lab")
        self.app.geometry("1000x500")

        # Buttons and Frame
        # Left Buttons
        self.btn_frame = ctk.CTkFrame(self.app)
        self.btn_frame.pack(side=tk.LEFT, fill="y", padx=10, pady=10)

        # Center
        self.canvas_frame = ctk.CTkFrame(self.app)
        self.canvas_frame.pack(side=tk.LEFT, expand=True, fill="both", padx=10, pady=10)

        # Spacer frame on top
        self.top_spacer = ctk.CTkFrame(self.canvas_frame, height=50)
        self.top_spacer.pack(side=tk.TOP, fill='x')
        self.top_spacer.configure(fg_color='#302c2c')

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=700,
            height=450,
            bg='#222222',
            highlightthickness=2,
            highlightbackground='white'
        )
        self.canvas.pack(expand=True)
        # self.canvas.configure(fg_color='#302c2c')
        
        # Spacer frame below
        self.bottom_spacer = ctk.CTkFrame(self.canvas_frame)
        self.bottom_spacer.pack(side=tk.TOP, expand=True, fill="both")
        self.bottom_spacer.configure(fg_color='#302c2c')

        # Right Buttons
        self.effect_frame = ctk.CTkFrame(self.app)
        self.effect_frame.pack(side=tk.LEFT, fill="y", padx=10, pady=10)

        # Images
        self.original_image = None
        self.current_image = None
        self.undo_stack = []
        self.redo_stack = []

        # Run
        self.create_buttons()
        self.create_effect_options()
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app.mainloop()


    # * Tkinter Window Setup
    def create_buttons(self):
        buttons = [
            ("Load Image", self.load_image),
            ("Save Image", self.save_image),
            ("Undo", self.undo_image),
            ("Redo", self.redo_image),
            ("Reset", self.reset_image)
        ]
     
        for text, command in buttons:
            button = ctk.CTkButton(self.btn_frame, text=text, command=command)
            button.pack(pady=5, side=tk.TOP)

    def create_effect_options(self):
        effects = [
            ("Brightness", self.adjust_brightness),
            ("Contrast", self.adjust_contrast),
            ("Saturation", self.adjust_saturation),
            ("Glitch", self.apply_glitch),
            ("Blur", self.apply_blur),
            ("Sharpen", self.apply_sharpen),
            ("Pixilate", self.apply_pixels),
            ("Invert Colors", self.apply_invert),
            ("Add Noise", self.apply_noise),
            ("Vignette", self.apply_vignette),
            ("Retro Filter", self.apply_retro_filter),
            ("Pencil Sketch", self.apply_pencil)
            # Thermal Camera
            # Face Swap if face detection
            # Gamma Correct
            # Sepia tone
        ]

        for text, command in effects:
            button = ctk.CTkButton(self.effect_frame, text=text, command=command)
            button.pack(side=tk.TOP, pady=3)

    # * Image  

    def load_image(self):
        file_path = load_image_via_dialog()
        if file_path:
            self.original_image = cv.imread(filename=file_path)
            self.current_image = self.original_image.copy()
            self.show_image(self.current_image)
            self.undo_stack.clear()
            self.redo_stack.clear()

    def save_image(self):
        if self.current_image is None:
            ctk_messagebox(title="Error", message="Please select an Image first")
            return
        save_image_via_dialog(self.current_image)

    def reset_image(self):
        if self.current_image is None:
            ctk_messagebox(title="Error", message="No Image to Reset")
            return
        self.add_to_undo_stack()
        self.current_image = self.original_image.copy()
        self.show_image(self.current_image)

    def undo_image(self):
        print("Trying to undo")
        if len(self.undo_stack) > 0:
            self.redo_stack.append(self.current_image.copy())
            self.current_image = self.undo_stack.pop()
            self.show_image(self.current_image)
        else:
            ctk_messagebox(title="Error", message="Still the original image")

    def add_to_undo_stack(self):
        self.undo_stack.append(self.current_image)
        self.redo_stack.clear()

    def redo_image(self):
        print("Trying to Redo")
        if len(self.redo_stack) > 0:
            self.undo_stack.append(self.current_image.copy())
            self.current_image = self.undo_stack.pop()
            self.show_image(self.current_image)
        else:
            ctk_messagebox(title="Error", message="Still the original image")
            

    # * Image Editing / Functions 

    def show_image(self, image):
        image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image_gray = cv.cvtColor(image_rgb, cv.COLOR_RGB2GRAY)
        image_pil = Image.fromarray(image_rgb)
        image_pil = image_pil.resize((700,450), Image.LANCZOS)
        image_tk = ImageTk.PhotoImage(image=image_pil)

        self.canvas.delete("all") 
        self.canvas.create_image(0,0, anchor='nw', image=image_tk)
        self.canvas.image_tk = image_tk

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            print("closed app")
            self.app.destroy()

    # image editing functions

    def adjust_brightness(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = adjust_brightness(self.current_image)
        self.show_image(self.current_image)

    def adjust_contrast(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = adjust_contrast(self.current_image)
        self.show_image(self.current_image)

    def adjust_saturation(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = adjust_saturation(self.current_image)
        self.show_image(self.current_image)

    def apply_glitch(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_glitch(self.current_image)
        self.show_image(self.current_image)

    def apply_blur(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_blur(self.current_image)
        self.show_image(self.current_image)

    def apply_sharpen(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_sharpen(self.current_image)
        self.show_image(self.current_image)

    def apply_pixels(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_pixels(self.current_image)
        self.show_image(self.current_image)

    def apply_invert(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_invert(self.current_image)
        self.show_image(self.current_image)

    def apply_noise(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_noise(self.current_image)
        self.show_image(self.current_image)

    def apply_vignette(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_vignette(self.current_image)
        self.show_image(self.current_image)

    def apply_retro_filter(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_retro_filter(self.current_image)
        self.show_image(self.current_image)

    def apply_pencil(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_pencil(self.current_image)
        self.show_image(self.current_image)