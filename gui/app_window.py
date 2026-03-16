'''
This file is responsible for:
Creating the Tkinter window and widgets (buttons, labels, canvas, etc.).
Handling user interactions (button clicks, sliders, etc.).
Displaying images (e.g., showing OpenCV processed images in the GUI).
Calling image processing functions when needed.
Managing the app’s main event loop.
'''

from utils.imports import (
    cv,
    np,
    tk,
    ctk,
    filedialog,
    messagebox,
    Image,
    ImageTk,
)
from utils.utils import load_image_via_dialog, save_image_via_dialog, check_image_loaded
from processing.image_filters import (
    adjust_brightness,
    adjust_saturation,
    adjust_contrast,
    adjust_brightness_with_factor,
    adjust_contrast_with_factor,
    adjust_saturation_with_factor,
    apply_glitch,
    apply_blur,
    apply_blur_with_radius,
    apply_sharpen,
    apply_pixels,
    apply_invert,
    apply_noise,
    apply_noise_with_intensity,
    apply_vignette,
    apply_retro_filter,
    apply_pencil,
    apply_smart_enhance,
)
from utils.customMessageBox import ctk_messagebox
import os


# Fix theme path for macOS compatibility
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get absolute path
theme_path = os.path.join(current_dir, '..', 'assets', 'theme.json')
# Ensure the path is absolute and exists
theme_path = os.path.abspath(theme_path)

class AppWindow:
    # * Initial Setup
    def __init__(self):
        ctk.set_appearance_mode("System")  
        
        # Add error handling for theme loading on macOS
        try:
            if os.path.exists(theme_path):
                ctk.set_default_color_theme(theme_path)
            else:
                print(f"Theme file not found at: {theme_path}")
                # Fall back to default theme
                ctk.set_default_color_theme("blue")
        except Exception as e:
            print(f"Error loading theme: {e}")
            # Fall back to default theme
            ctk.set_default_color_theme("blue")

        self.app = ctk.CTk()
        self.app.title("Image Lab")
        self.app.geometry("1000x500")

        # macOS-specific window configuration
        if hasattr(self.app, '_set_appearance_mode'):
            try:
                self.app._set_appearance_mode("System")
            except:
                pass

        self.tabview = ctk.CTkTabview(master=self.app)
        self.tabview.pack()

        self.tabview.add("Photo Editor")  # add tab at the end
        self.tabview.add("Batch Tools")  # new batch tab
        self.tabview.add("Settings")  # add tab at the end
        self.tabview.set("Photo Editor")  # set currently visible tab

        # Buttons and Frame
        # Left Buttons + history column
        self.btn_frame = ctk.CTkFrame(self.tabview.tab("Photo Editor"))
        self.btn_frame.pack(side=tk.LEFT, fill="y", padx=10, pady=10)

        # History panel under buttons
        self.history_frame = ctk.CTkScrollableFrame(self.btn_frame, label_text="History")
        self.history_frame.pack(side=tk.BOTTOM, fill="both", expand=True, pady=(10, 0))
        self.history_entries = []

        # Center
        self.canvas_frame = ctk.CTkFrame(self.tabview.tab("Photo Editor"))
        self.canvas_frame.pack(side=tk.LEFT, expand=True, fill="both", padx=10, pady=10)

        # Spacer frame on top
        self.top_spacer = ctk.CTkFrame(self.canvas_frame, height=50)
        self.top_spacer.pack(side=tk.TOP, fill='x')
        # self.top_spacer.configure(fg_color='#302c2c')

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
        # self.bottom_spacer.configure(fg_color='#302c2c')

        # Right Buttons (effects)
        self.effect_frame = ctk.CTkFrame(self.tabview.tab("Photo Editor"))
        self.effect_frame.pack(side=tk.LEFT, fill="y", padx=10, pady=10)

        # Far-right control panel for sliders
        self.control_frame = ctk.CTkFrame(self.tabview.tab("Photo Editor"))
        self.control_frame.pack(side=tk.LEFT, fill="y", padx=10, pady=10)

        # Images
        self.original_image = None
        self.current_image = None
        self.undo_stack = []
        self.redo_stack = []
        self.preview_base_image = None
        self.recent_files = []

        # Run
        self.create_buttons()
        self.create_effect_options()
        self.create_control_panel()
        self.create_batch_tab()
        self.create_settings_tab()
        self._bind_shortcuts()
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

        # Tutorial Button
        tut_button = ctk.CTkButton(self.btn_frame, text="Tutorial", command=self.open_tutorial)
        tut_button.pack(pady=5, side=tk.TOP)

    def open_tutorial(self):
        pass

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
            ("Pencil Sketch", self.apply_pencil),
            ("Smart Enhance", self.apply_smart_enhance)
            # Thermal Camera
            # Face Swap if face detection
            # Gamma Correct
            # Sepia tone
        ]

        for text, command in effects:
            button = ctk.CTkButton(self.effect_frame, text=text, command=command)
            button.pack(side=tk.TOP, pady=3)

    def create_batch_tab(self):
        """Create UI for batch processing tools."""
        tab = self.tabview.tab("Batch Tools")

        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        input_label = ctk.CTkLabel(frame, text="Input folder")
        input_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.batch_input_entry = ctk.CTkEntry(frame, width=350)
        self.batch_input_entry.grid(row=1, column=0, sticky="w")
        input_btn = ctk.CTkButton(frame, text="Browse…", command=self._choose_batch_input)
        input_btn.grid(row=1, column=1, padx=(10, 0))

        output_label = ctk.CTkLabel(frame, text="Output folder")
        output_label.grid(row=2, column=0, sticky="w", pady=(15, 5))
        self.batch_output_entry = ctk.CTkEntry(frame, width=350)
        self.batch_output_entry.grid(row=3, column=0, sticky="w")
        output_btn = ctk.CTkButton(frame, text="Browse…", command=self._choose_batch_output)
        output_btn.grid(row=3, column=1, padx=(10, 0))

        # Options
        self.batch_retro_var = tk.BooleanVar(value=True)
        self.batch_sharpen_var = tk.BooleanVar(value=True)
        self.batch_blur_var = tk.BooleanVar(value=False)

        retro_chk = ctk.CTkCheckBox(frame, text="Apply Retro Filter", variable=self.batch_retro_var)
        retro_chk.grid(row=4, column=0, sticky="w", pady=(20, 5))
        sharpen_chk = ctk.CTkCheckBox(frame, text="Apply Sharpen", variable=self.batch_sharpen_var)
        sharpen_chk.grid(row=5, column=0, sticky="w", pady=5)
        blur_chk = ctk.CTkCheckBox(frame, text="Apply Blur", variable=self.batch_blur_var)
        blur_chk.grid(row=6, column=0, sticky="w", pady=5)

        self.batch_blur_slider = ctk.CTkSlider(frame, from_=0, to=10, number_of_steps=10)
        self.batch_blur_slider.set(3)
        self.batch_blur_slider.grid(row=7, column=0, sticky="we", pady=(0, 10))

        run_btn = ctk.CTkButton(frame, text="Run Batch Processing", command=self._run_batch_processing)
        run_btn.grid(row=8, column=0, columnspan=2, sticky="we", pady=(20, 0))

        # Recent files display (read-only)
        recent_label = ctk.CTkLabel(frame, text="Recent files this session")
        recent_label.grid(row=0, column=2, sticky="w", padx=(40, 0))
        self.recent_files_box = ctk.CTkTextbox(frame, width=260, height=180)
        self.recent_files_box.grid(row=1, column=2, rowspan=8, sticky="nsew", padx=(40, 0))
        self.recent_files_box.configure(state="disabled")

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(2, weight=0)

    def create_settings_tab(self):
        """Create basic settings UI."""
        tab = self.tabview.tab("Settings")

        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Notification settings
        notif_label = ctk.CTkLabel(frame, text="Notifications", font=("Arial", 14, "bold"))
        notif_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.show_success_toasts = tk.BooleanVar(value=True)
        self.show_error_dialogs = tk.BooleanVar(value=True)

        success_chk = ctk.CTkCheckBox(frame, text="Show success popups (e.g., after save/apply)", variable=self.show_success_toasts)
        success_chk.grid(row=1, column=0, sticky="w", pady=2)

        error_chk = ctk.CTkCheckBox(frame, text="Show error dialogs", variable=self.show_error_dialogs)
        error_chk.grid(row=2, column=0, sticky="w", pady=2)

        # Display size settings
        display_label = ctk.CTkLabel(frame, text="Display", font=("Arial", 14, "bold"))
        display_label.grid(row=3, column=0, sticky="w", pady=(20, 5))

        self.display_mode = tk.StringVar(value="fit-width")
        fit_width_radio = ctk.CTkRadioButton(frame, text="Fit to width", variable=self.display_mode, value="fit-width")
        fit_width_radio.grid(row=4, column=0, sticky="w", pady=2)
        fit_window_radio = ctk.CTkRadioButton(frame, text="Fit to window", variable=self.display_mode, value="fit-window")
        fit_window_radio.grid(row=5, column=0, sticky="w", pady=2)

        # Placeholder for future TTS toggle
        tts_label = ctk.CTkLabel(frame, text="TTS / Sound (future)", font=("Arial", 14, "bold"))
        tts_label.grid(row=6, column=0, sticky="w", pady=(20, 5))
        self.tts_enabled = tk.BooleanVar(value=False)
        tts_chk = ctk.CTkCheckBox(frame, text="Enable spoken feedback (planned)", variable=self.tts_enabled, state="disabled")
        tts_chk.grid(row=7, column=0, sticky="w", pady=2)

    def create_control_panel(self):
        """Create slider-based controls for key adjustments on the right side."""
        title_label = ctk.CTkLabel(self.control_frame, text="Adjustments", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))

        # Brightness slider
        self.brightness_label = ctk.CTkLabel(self.control_frame, text="Brightness")
        self.brightness_label.pack()
        self.brightness_slider = ctk.CTkSlider(self.control_frame, from_=0.0, to=2.0, number_of_steps=100,
                                               command=self.on_brightness_change)
        self.brightness_slider.set(1.0)
        self.brightness_slider.pack(fill="x", pady=(0, 5))
        brightness_button = ctk.CTkButton(self.control_frame, text="Apply Brightness", command=self.apply_brightness_from_slider)
        brightness_button.pack(pady=(0, 10), fill="x")

        # Contrast slider
        self.contrast_label = ctk.CTkLabel(self.control_frame, text="Contrast")
        self.contrast_label.pack()
        self.contrast_slider = ctk.CTkSlider(self.control_frame, from_=0.0, to=2.0, number_of_steps=100,
                                             command=self.on_contrast_change)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill="x", pady=(0, 5))
        contrast_button = ctk.CTkButton(self.control_frame, text="Apply Contrast", command=self.apply_contrast_from_slider)
        contrast_button.pack(pady=(0, 10), fill="x")

        # Saturation slider
        self.saturation_label = ctk.CTkLabel(self.control_frame, text="Saturation")
        self.saturation_label.pack()
        self.saturation_slider = ctk.CTkSlider(self.control_frame, from_=0.0, to=2.0, number_of_steps=100)
        self.saturation_slider.set(1.0)
        self.saturation_slider.pack(fill="x", pady=(0, 5))
        saturation_button = ctk.CTkButton(self.control_frame, text="Apply Saturation", command=self.apply_saturation_from_slider)
        saturation_button.pack(pady=(0, 10), fill="x")

        # Blur slider
        self.blur_label = ctk.CTkLabel(self.control_frame, text="Blur Radius")
        self.blur_label.pack()
        self.blur_slider = ctk.CTkSlider(self.control_frame, from_=0, to=10, number_of_steps=10)
        self.blur_slider.set(0)
        self.blur_slider.pack(fill="x", pady=(0, 5))
        blur_button = ctk.CTkButton(self.control_frame, text="Apply Blur", command=self.apply_blur_from_slider)
        blur_button.pack(pady=(0, 10), fill="x")

        # Noise slider
        self.noise_label = ctk.CTkLabel(self.control_frame, text="Noise Intensity")
        self.noise_label.pack()
        self.noise_slider = ctk.CTkSlider(self.control_frame, from_=0.0, to=1.0, number_of_steps=20)
        self.noise_slider.set(0.0)
        self.noise_slider.pack(fill="x", pady=(0, 5))
        noise_button = ctk.CTkButton(self.control_frame, text="Apply Noise", command=self.apply_noise_from_slider)
        noise_button.pack(pady=(0, 10), fill="x")

    # * Image  

    def load_image(self):
        file_path = load_image_via_dialog()
        if file_path:
            self.original_image = cv.imread(filename=file_path)
            self.current_image = self.original_image.copy()
            self.preview_base_image = None
            self.show_image(self.current_image)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.clear_history()
            self._add_recent_file(file_path)

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
        self.preview_base_image = None
        self.add_history_entry("Reset to original")

    def undo_image(self):
        print("Trying to undo")
        if len(self.undo_stack) > 0:
            self.redo_stack.append(self.current_image.copy())
            self.current_image = self.undo_stack.pop()
            self.show_image(self.current_image)
            self.preview_base_image = None
            self.add_history_entry("Undo")
        else:
            ctk_messagebox(title="Error", message="Still the original image")

    def add_to_undo_stack(self):
        self.undo_stack.append(self.current_image)
        self.redo_stack.clear()

    def redo_image(self):
        print("Trying to Redo")
        if len(self.redo_stack) > 0:
            self.undo_stack.append(self.current_image.copy())
            self.current_image = self.redo_stack.pop()
            self.show_image(self.current_image)
            self.preview_base_image = None
            self.add_history_entry("Redo")
        else:
            ctk_messagebox(title="Error", message="Still the original image")
            

    # * Image Editing / Functions 

    def show_image(self, image):
        image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
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
        self.preview_base_image = None
        self.add_history_entry("Brightness (dialog)")

    def adjust_contrast(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = adjust_contrast(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Contrast (dialog)")

    def adjust_saturation(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = adjust_saturation(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Saturation (dialog)")

    def apply_glitch(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_glitch(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Glitch")

    def apply_blur(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_blur(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Blur (dialog)")

    def apply_sharpen(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_sharpen(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Sharpen")

    def apply_pixels(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_pixels(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Pixilate")

    def apply_invert(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_invert(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Invert")

    def apply_noise(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_noise(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Noise (dialog)")

    def apply_vignette(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_vignette(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Vignette")

    def apply_retro_filter(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_retro_filter(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Retro filter")

    def apply_pencil(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_pencil(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Pencil sketch")

    def apply_smart_enhance(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        self.current_image = apply_smart_enhance(self.current_image)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Smart Enhance")

    # Slider-based adjustment handlers

    def apply_brightness_from_slider(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        factor = self.brightness_slider.get()
        self.current_image = adjust_brightness_with_factor(self.current_image, factor)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Brightness slider: {factor:.2f}")

    def apply_contrast_from_slider(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        factor = self.contrast_slider.get()
        self.current_image = adjust_contrast_with_factor(self.current_image, factor)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Contrast slider: {factor:.2f}")

    def apply_saturation_from_slider(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        factor = self.saturation_slider.get()
        self.current_image = adjust_saturation_with_factor(self.current_image, factor)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Saturation slider: {factor:.2f}")

    def apply_blur_from_slider(self):
        if not check_image_loaded(self.current_image):
            return
        radius = self.blur_slider.get()
        if radius <= 0:
            # No blur requested
            return
        self.add_to_undo_stack()
        self.current_image = apply_blur_with_radius(self.current_image, radius)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Blur slider: {radius:.1f}")

    def apply_noise_from_slider(self):
        if not check_image_loaded(self.current_image):
            return
        intensity = self.noise_slider.get()
        if intensity <= 0:
            # No additional noise
            return
        self.add_to_undo_stack()
        self.current_image = apply_noise_with_intensity(self.current_image, intensity)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Noise slider: {intensity:.2f}")

    # Live preview callbacks for sliders (brightness & contrast)

    def on_brightness_change(self, value):
        if self.current_image is None:
            return
        if self.preview_base_image is None:
            self.preview_base_image = self.current_image.copy()
        factor = float(value)
        preview = adjust_brightness_with_factor(self.preview_base_image, factor)
        self.show_image(preview)

    def on_contrast_change(self, value):
        if self.current_image is None:
            return
        if self.preview_base_image is None:
            self.preview_base_image = self.current_image.copy()
        factor = float(value)
        preview = adjust_contrast_with_factor(self.preview_base_image, factor)
        self.show_image(preview)

    # History helpers

    def add_history_entry(self, text: str):
        label = ctk.CTkLabel(self.history_frame, text=text, anchor="w")
        label.pack(fill="x", padx=5, pady=2)
        self.history_entries.append(label)

    def clear_history(self):
        for lbl in self.history_entries:
            lbl.destroy()
        self.history_entries = []

    # Recent files helpers

    def _add_recent_file(self, path: str, max_items: int = 10):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:max_items]
        self._refresh_recent_files_box()

    def _refresh_recent_files_box(self):
        if not hasattr(self, "recent_files_box"):
            return
        self.recent_files_box.configure(state="normal")
        self.recent_files_box.delete("1.0", "end")
        for p in self.recent_files:
            self.recent_files_box.insert("end", p + "\n")
        self.recent_files_box.configure(state="disabled")

    # Batch tools callbacks

    def _choose_batch_input(self):
        folder = filedialog.askdirectory(title="Select input folder")
        if folder:
            self.batch_input_entry.delete(0, "end")
            self.batch_input_entry.insert(0, folder)

    def _choose_batch_output(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.batch_output_entry.delete(0, "end")
            self.batch_output_entry.insert(0, folder)

    def _run_batch_processing(self):
        from processing.batch import process_folder_basic

        input_folder = self.batch_input_entry.get().strip()
        output_folder = self.batch_output_entry.get().strip()
        if not input_folder or not output_folder:
            ctk_messagebox(title="Error", message="Please choose both input and output folders.")
            return

        apply_retro = self.batch_retro_var.get()
        apply_sharpen_flag = self.batch_sharpen_var.get()
        blur_radius = self.batch_blur_slider.get() if self.batch_blur_var.get() else None

        process_folder_basic(
            input_folder=input_folder,
            output_folder=output_folder,
            apply_retro=apply_retro,
            apply_sharpen_flag=apply_sharpen_flag,
            blur_radius=blur_radius,
        )

        ctk_messagebox(title="Batch complete", message="Finished processing images in the folder.")

    # Keyboard shortcuts

    def _bind_shortcuts(self):
        # File operations
        self.app.bind("<Command-o>", lambda event: self.load_image())
        self.app.bind("<Control-o>", lambda event: self.load_image())
        self.app.bind("<Command-s>", lambda event: self.save_image())
        self.app.bind("<Control-s>", lambda event: self.save_image())

        # History operations
        self.app.bind("<Command-z>", lambda event: self.undo_image())
        self.app.bind("<Control-z>", lambda event: self.undo_image())
        self.app.bind("<Shift-Command-Z>", lambda event: self.redo_image())
        self.app.bind("<Control-y>", lambda event: self.redo_image())

        # Reset
        self.app.bind("<Command-r>", lambda event: self.reset_image())
        self.app.bind("<Control-r>", lambda event: self.reset_image())

        # A couple of quick filters
        self.app.bind("<Command-b>", lambda event: self.apply_blur())
        self.app.bind("<Control-b>", lambda event: self.apply_blur())
        self.app.bind("<Command-e>", lambda event: self.apply_smart_enhance())
        self.app.bind("<Control-e>", lambda event: self.apply_smart_enhance())