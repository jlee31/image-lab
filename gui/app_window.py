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

class AppWindow:
    # * Initial Setup
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("Image Lab")
        self.app.geometry("1000x700")

        # Buttons and Frame

        self.btn_frame = tk.Frame(self.app)
        self.btn_frame.pack(pady=5)

        self.effect_frame = tk.Frame(self.app)
        self.effect_frame.pack(pady=5)

        self.canvas_frame = tk.Frame(self.app)
        self.canvas_frame.pack(pady=10)

        self.canvas = tk.Canvas(self.canvas_frame, width=700, height=450, bg='gray90')
        self.canvas.pack()

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
        pass

    def create_effect_options(self):
        pass

    # * Image  

    def reset_image(self):
        pass

    def undo_image(self):
        pass

    def redo_image(self):
        pass

    # * Image Editing / Functions 

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            print("closed app")
            self.app.destroy()

