'''
This file is responsible for:
Creating the Tkinter window and widgets (buttons, labels, canvas, etc.).
Handling user interactions (button clicks, sliders, etc.).
Displaying images (e.g., showing OpenCV processed images in the GUI).
Calling image processing functions when needed.
Managing the app's main event loop.
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


class AppWindow:
    # ── Colour palette ───────────────────────────────────────────────────────
    BG            = "#F5F5F7"
    CARD          = "#FFFFFF"
    PRIMARY       = "#18181B"
    PRIMARY_HOVER = "#374151"
    BORDER        = "#E5E7EB"
    TEXT          = "#18181B"
    TEXT_SEC      = "#374151"
    TEXT_MUTED    = "#9CA3AF"
    ACCENT        = "#7C3AED"
    ACCENT_LIGHT  = "#EDE9F6"

    # ── Tab name constants ───────────────────────────────────────────────────
    TAB_EDITOR   = "  🖼  Photo Editor  "
    TAB_BATCH    = "  ⊞  Batch Tools  "
    TAB_SETTINGS = "  ⚙  Settings  "

    def __init__(self):
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.app = ctk.CTk()
        self.app.title("Image Lab")
        self.app.geometry("1280x760")
        self.app.minsize(900, 600)
        self.app.configure(fg_color=self.BG)

        # Image state
        self.original_image    = None
        self.current_image     = None
        self.undo_stack        = []
        self.redo_stack        = []
        self.preview_base_image = None
        self.recent_files      = []
        self.history_entries   = []
        self._history_visible  = False

        # Settings vars (initialised here so they exist before settings tab)
        self.show_success_toasts = tk.BooleanVar(value=True)
        self.show_error_dialogs  = tk.BooleanVar(value=True)
        self.display_mode        = tk.StringVar(value="fit-window")
        self.tts_enabled         = tk.BooleanVar(value=False)

        # Re-render current image whenever display mode changes
        self.display_mode.trace_add("write", lambda *_: self._on_display_mode_change())

        # Build UI
        self._create_header()
        self._create_tabs()
        self._create_photo_editor_tab()
        self._create_batch_tab()
        self._create_settings_tab()
        self._bind_shortcuts()

        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app.mainloop()

    # ── Header ───────────────────────────────────────────────────────────────

    def _create_header(self):
        header = ctk.CTkFrame(self.app, fg_color=self.CARD, corner_radius=0, height=72)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # App icon
        icon_bg = ctk.CTkFrame(header, fg_color=self.ACCENT, width=44, height=44, corner_radius=10)
        icon_bg.pack(side="left", padx=(20, 10), pady=14)
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="🖼", font=("Arial", 22), text_color="white").pack(expand=True)

        # Title + subtitle
        text_col = ctk.CTkFrame(header, fg_color="transparent")
        text_col.pack(side="left", pady=14)
        ctk.CTkLabel(text_col, text="Image Lab",
                     font=("Arial", 19, "bold"), text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(text_col, text="Professional photo editing suite",
                     font=("Arial", 11), text_color=self.TEXT_MUTED).pack(anchor="w")

        # Bottom border
        ctk.CTkFrame(self.app, fg_color=self.BORDER, height=1, corner_radius=0).pack(fill="x")

    # ── Tab bar ──────────────────────────────────────────────────────────────

    def _create_tabs(self):
        self.tabview = ctk.CTkTabview(
            self.app,
            fg_color=self.BG,
            segmented_button_fg_color=self.BG,
            segmented_button_selected_color=self.CARD,
            segmented_button_selected_hover_color=self.CARD,
            segmented_button_unselected_color=self.BG,
            segmented_button_unselected_hover_color="#EBEBED",
            text_color=self.TEXT_SEC,
        )
        self.tabview.pack(fill="both", expand=True)
        self.tabview.add(self.TAB_EDITOR)
        self.tabview.add(self.TAB_BATCH)
        self.tabview.add(self.TAB_SETTINGS)
        self.tabview.set(self.TAB_EDITOR)

    # ── Photo Editor tab ─────────────────────────────────────────────────────

    def _create_photo_editor_tab(self):
        tab = self.tabview.tab(self.TAB_EDITOR)
        tab.configure(fg_color=self.BG)

        # Left sidebar
        self.left_sidebar = ctk.CTkFrame(tab, fg_color=self.CARD, corner_radius=12, width=215)
        self.left_sidebar.pack(side="left", fill="y", padx=(10, 5), pady=10)
        self.left_sidebar.pack_propagate(False)

        # Right panel (scrollable)
        self.right_panel = ctk.CTkScrollableFrame(
            tab, fg_color=self.BG, width=295, corner_radius=0,
            scrollbar_button_color=self.BORDER,
            scrollbar_button_hover_color="#D1D5DB",
        )
        self.right_panel.pack(side="right", fill="y", padx=(5, 10), pady=10)

        # Centre canvas area
        self.canvas_frame = ctk.CTkFrame(tab, fg_color=self.CARD, corner_radius=12)
        self.canvas_frame.pack(side="left", fill="both", expand=True, padx=5, pady=10)

        self._build_left_sidebar()
        self._build_canvas_area()
        self._build_right_panel()

    # ── Left sidebar ─────────────────────────────────────────────────────────

    def _build_left_sidebar(self):
        sb = self.left_sidebar

        ctk.CTkLabel(sb, text="Quick Actions",
                     font=("Arial", 12, "bold"), text_color=self.TEXT
                     ).pack(anchor="w", padx=15, pady=(16, 8))

        self._sb_btn(sb, "↑   Load Image", self.load_image, primary=True)
        self._sb_btn(sb, "↓   Save Image", self.save_image)

        self._divider(sb)

        ctk.CTkLabel(sb, text="History",
                     font=("Arial", 12, "bold"), text_color=self.TEXT
                     ).pack(anchor="w", padx=15, pady=(4, 8))

        self._sb_btn(sb, "↩   Undo",      self.undo_image)
        self._sb_btn(sb, "↪   Redo",      self.redo_image)
        self._sb_btn(sb, "↺   Reset All", self.reset_image)

        self._divider(sb)

        self._sb_btn(sb, "📖   Tutorial",     self.open_tutorial,     ghost=True)
        self._sb_btn(sb, "🕐   View History", self._toggle_history,   ghost=True)

        # Edit-history log — hidden until user clicks View History
        self.history_frame = ctk.CTkScrollableFrame(
            sb, label_text="Edit History", fg_color="#F9FAFB", corner_radius=8,
            label_font=("Arial", 11, "bold"), label_text_color=self.TEXT_SEC,
            height=160,
        )

    def _sb_btn(self, parent, text, command, *, primary=False, ghost=False):
        if primary:
            kw = dict(fg_color=self.PRIMARY, hover_color=self.PRIMARY_HOVER,
                      text_color="white")
        elif ghost:
            kw = dict(fg_color="transparent", hover_color="#F5F5F7",
                      text_color=self.TEXT_SEC)
        else:
            kw = dict(fg_color=self.CARD, hover_color="#F5F5F7",
                      text_color=self.TEXT, border_width=1, border_color=self.BORDER)

        btn = ctk.CTkButton(parent, text=text, command=command,
                            corner_radius=8, height=36, anchor="w", **kw)
        btn.pack(fill="x", padx=15, pady=(0, 6))
        return btn

    def _divider(self, parent):
        ctk.CTkFrame(parent, fg_color=self.BORDER, height=1).pack(fill="x", padx=15, pady=8)

    def _toggle_history(self):
        if self._history_visible:
            self.history_frame.pack_forget()
            self._history_visible = False
        else:
            self.history_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            self._history_visible = True

    # ── Canvas ───────────────────────────────────────────────────────────────

    def _build_canvas_area(self):
        # Empty state — shown when no image is loaded
        self._empty_frame = ctk.CTkFrame(self.canvas_frame, fg_color=self.CARD, corner_radius=0)
        self._empty_frame.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(self._empty_frame, fg_color="transparent")
        inner.place(relx=0.5, rely=0.45, anchor="center")

        circle = ctk.CTkFrame(inner, fg_color=self.ACCENT_LIGHT, width=116, height=116, corner_radius=58)
        circle.pack()
        circle.pack_propagate(False)
        ctk.CTkLabel(circle, text="📷", font=("Arial", 44)).pack(expand=True)

        ctk.CTkLabel(inner, text="No Image Loaded",
                     font=("Arial", 17, "bold"), text_color=self.TEXT).pack(pady=(20, 0))
        ctk.CTkLabel(inner,
                     text="Upload an image to start editing with our\nprofessional tools",
                     font=("Arial", 11), text_color=self.TEXT_MUTED, justify="center").pack(pady=(8, 20))
        ctk.CTkButton(inner, text="↑   Choose Image", command=self.load_image,
                      fg_color=self.PRIMARY, hover_color=self.PRIMARY_HOVER,
                      text_color="white", corner_radius=8, height=40, width=160).pack()

        # Canvas — shown once an image is loaded (hidden initially)
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.CARD, highlightthickness=0)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _on_canvas_resize(self, _event):
        if self.current_image is not None:
            self.show_image(self.current_image)

    def _show_canvas(self):
        """Switch from empty state to canvas."""
        self._empty_frame.pack_forget()
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)

    def _on_display_mode_change(self):
        if self.current_image is not None:
            self.show_image(self.current_image)

    # ── Right panel ──────────────────────────────────────────────────────────

    def _build_right_panel(self):
        ctk.CTkLabel(self.right_panel, text="Adjustments & Filters",
                     font=("Arial", 15, "bold"), text_color=self.TEXT
                     ).pack(anchor="w", pady=(4, 10))

        adj_content = self._collapsible_card(self.right_panel, "✦   Basic Adjustments")
        self._build_basic_adjustments(adj_content)

        filt_content = self._collapsible_card(self.right_panel, "▼   Creative Filters")
        self._build_creative_filters(filt_content)

    def _collapsible_card(self, parent, title):
        """Returns the content frame of a collapsible white card."""
        card = ctk.CTkFrame(parent, fg_color=self.CARD, corner_radius=12)
        card.pack(fill="x", pady=(0, 10))
        is_open = [True]

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(12, 0))

        ctk.CTkLabel(hdr, text=title,
                     font=("Arial", 13, "bold"), text_color=self.TEXT).pack(side="left")

        toggle_btn = ctk.CTkButton(
            hdr, text="∧", width=28, height=28,
            fg_color="transparent", hover_color=self.BG,
            text_color=self.TEXT_MUTED, font=("Arial", 15, "bold"),
            corner_radius=6,
        )
        toggle_btn.pack(side="right")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=14, pady=(6, 14))

        def toggle():
            if is_open[0]:
                content.pack_forget()
                toggle_btn.configure(text="∨")
                is_open[0] = False
            else:
                content.pack(fill="x", padx=14, pady=(6, 14))
                toggle_btn.configure(text="∧")
                is_open[0] = True

        toggle_btn.configure(command=toggle)
        return content

    def _build_basic_adjustments(self, parent):
        # (icon, label, from, to, initial, steps, fmt_fn, slider_attr, live_cb, release_cb)
        cfg = [
            ("☀", "Brightness", 0.0, 2.0, 1.0, 100,
             lambda v: f"{int(float(v) * 100)}%", "brightness_slider",
             self.on_brightness_change, self.apply_brightness_from_slider),
            ("◑", "Contrast", 0.0, 2.0, 1.0, 100,
             lambda v: f"{int(float(v) * 100)}%", "contrast_slider",
             self.on_contrast_change, self.apply_contrast_from_slider),
            ("💧", "Saturation", 0.0, 2.0, 1.0, 100,
             lambda v: f"{int(float(v) * 100)}%", "saturation_slider",
             None, self.apply_saturation_from_slider),
            ("◎", "Blur Radius", 0, 10, 0, 10,
             lambda v: f"{int(float(v))}px", "blur_slider",
             None, self.apply_blur_from_slider),
            ("⊞", "Noise Intensity", 0.0, 1.0, 0.0, 20,
             lambda v: f"{int(float(v) * 100)}%", "noise_slider",
             None, self.apply_noise_from_slider),
        ]

        for icon, label, from_, to, initial, steps, fmt, attr, live_cb, release_cb in cfg:
            # Label row
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=(8, 0))

            ctk.CTkLabel(row, text=f"{icon}  {label}",
                         font=("Arial", 12), text_color=self.TEXT_SEC).pack(side="left")

            val_lbl = ctk.CTkLabel(row, text=fmt(initial),
                                   font=("Arial", 12), text_color=self.TEXT_MUTED)
            val_lbl.pack(side="right")

            def _make_cmd(vl, f, live):
                def cmd(value):
                    vl.configure(text=f(value))
                    if live:
                        live(value)
                return cmd

            slider = ctk.CTkSlider(
                parent, from_=from_, to=to, number_of_steps=steps,
                fg_color=self.BORDER,
                progress_color=self.PRIMARY,
                button_color=self.PRIMARY,
                button_hover_color=self.PRIMARY_HOVER,
                command=_make_cmd(val_lbl, fmt, live_cb),
            )
            slider.set(initial)
            slider.pack(fill="x", pady=(4, 0))
            slider.bind("<ButtonRelease-1>", lambda e, cb=release_cb: cb())

            setattr(self, attr, slider)

    def _build_creative_filters(self, parent):
        filters = [
            ("⚡", "Glitch Effect",  self.apply_glitch),
            ("✨", "Sharpen",        self.apply_sharpen),
            ("⊙", "Invert Colors",  self.apply_invert),
            ("◉", "Vignette",       self.apply_vignette),
            ("▦", "Pixelate",       self.apply_pixels),
            ("↻", "Retro Filter",   self.apply_retro_filter),
            ("✏", "Pencil Sketch",  self.apply_pencil),
            ("⚙", "Smart Enhance",  self.apply_smart_enhance),
        ]
        for icon, name, cmd in filters:
            ctk.CTkButton(
                parent, text=f"{icon}   {name}", command=cmd,
                fg_color=self.CARD, hover_color=self.BG,
                text_color=self.TEXT_SEC,
                border_width=1, border_color=self.BORDER,
                corner_radius=8, height=36, anchor="w",
            ).pack(fill="x", pady=(0, 6))

    # ── Batch Tools tab ──────────────────────────────────────────────────────

    def _create_batch_tab(self):
        tab = self.tabview.tab(self.TAB_BATCH)
        tab.configure(fg_color=self.BG)

        card = ctk.CTkFrame(tab, fg_color=self.CARD, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        frame = ctk.CTkFrame(card, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Input folder",
                     font=("Arial", 12), text_color=self.TEXT
                     ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.batch_input_entry = ctk.CTkEntry(frame, width=350, border_color=self.BORDER)
        self.batch_input_entry.grid(row=1, column=0, sticky="w")
        ctk.CTkButton(frame, text="Browse…", command=self._choose_batch_input,
                      fg_color=self.PRIMARY, hover_color=self.PRIMARY_HOVER
                      ).grid(row=1, column=1, padx=(10, 0))

        ctk.CTkLabel(frame, text="Output folder",
                     font=("Arial", 12), text_color=self.TEXT
                     ).grid(row=2, column=0, sticky="w", pady=(15, 5))
        self.batch_output_entry = ctk.CTkEntry(frame, width=350, border_color=self.BORDER)
        self.batch_output_entry.grid(row=3, column=0, sticky="w")
        ctk.CTkButton(frame, text="Browse…", command=self._choose_batch_output,
                      fg_color=self.PRIMARY, hover_color=self.PRIMARY_HOVER
                      ).grid(row=3, column=1, padx=(10, 0))

        self.batch_retro_var   = tk.BooleanVar(value=True)
        self.batch_sharpen_var = tk.BooleanVar(value=True)
        self.batch_blur_var    = tk.BooleanVar(value=False)

        ctk.CTkCheckBox(frame, text="Apply Retro Filter",
                        variable=self.batch_retro_var
                        ).grid(row=4, column=0, sticky="w", pady=(20, 5))
        ctk.CTkCheckBox(frame, text="Apply Sharpen",
                        variable=self.batch_sharpen_var
                        ).grid(row=5, column=0, sticky="w", pady=5)
        ctk.CTkCheckBox(frame, text="Apply Blur",
                        variable=self.batch_blur_var
                        ).grid(row=6, column=0, sticky="w", pady=5)

        self.batch_blur_slider = ctk.CTkSlider(
            frame, from_=0, to=10, number_of_steps=10,
            fg_color=self.BORDER, progress_color=self.PRIMARY,
            button_color=self.PRIMARY, button_hover_color=self.PRIMARY_HOVER,
        )
        self.batch_blur_slider.set(3)
        self.batch_blur_slider.grid(row=7, column=0, sticky="we", pady=(0, 10))

        ctk.CTkButton(frame, text="Run Batch Processing",
                      command=self._run_batch_processing,
                      fg_color=self.PRIMARY, hover_color=self.PRIMARY_HOVER
                      ).grid(row=8, column=0, columnspan=2, sticky="we", pady=(20, 0))

        ctk.CTkLabel(frame, text="Recent files this session",
                     font=("Arial", 12), text_color=self.TEXT
                     ).grid(row=0, column=2, sticky="w", padx=(40, 0))
        self.recent_files_box = ctk.CTkTextbox(
            frame, width=260, height=180,
            border_color=self.BORDER, border_width=1,
        )
        self.recent_files_box.grid(row=1, column=2, rowspan=8, sticky="nsew", padx=(40, 0))
        self.recent_files_box.configure(state="disabled")

        frame.grid_columnconfigure(0, weight=1)

    # ── Settings tab ─────────────────────────────────────────────────────────

    def _create_settings_tab(self):
        tab = self.tabview.tab(self.TAB_SETTINGS)
        tab.configure(fg_color=self.BG)

        card = ctk.CTkFrame(tab, fg_color=self.CARD, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        frame = ctk.CTkFrame(card, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Notifications",
                     font=("Arial", 14, "bold"), text_color=self.TEXT
                     ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        ctk.CTkCheckBox(frame, text="Show success popups (e.g., after save/apply)",
                        variable=self.show_success_toasts
                        ).grid(row=1, column=0, sticky="w", pady=2)
        ctk.CTkCheckBox(frame, text="Show error dialogs",
                        variable=self.show_error_dialogs
                        ).grid(row=2, column=0, sticky="w", pady=2)

        ctk.CTkLabel(frame, text="Display",
                     font=("Arial", 14, "bold"), text_color=self.TEXT
                     ).grid(row=3, column=0, sticky="w", pady=(20, 5))
        ctk.CTkRadioButton(frame, text="Fit to width",
                           variable=self.display_mode, value="fit-width"
                           ).grid(row=4, column=0, sticky="w", pady=2)
        ctk.CTkRadioButton(frame, text="Fit to window",
                           variable=self.display_mode, value="fit-window"
                           ).grid(row=5, column=0, sticky="w", pady=2)

        ctk.CTkLabel(frame, text="TTS / Sound (future)",
                     font=("Arial", 14, "bold"), text_color=self.TEXT
                     ).grid(row=6, column=0, sticky="w", pady=(20, 5))
        ctk.CTkCheckBox(frame, text="Enable spoken feedback (planned)",
                        variable=self.tts_enabled, state="disabled"
                        ).grid(row=7, column=0, sticky="w", pady=2)

    # ── Image loading / saving ────────────────────────────────────────────────

    def load_image(self):
        file_path = load_image_via_dialog()
        if file_path:
            self.original_image = cv.imread(filename=file_path)
            self.current_image  = self.original_image.copy()
            self.preview_base_image = None
            self._show_canvas()
            self.show_image(self.current_image)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.clear_history()
            self._add_recent_file(file_path)

    def save_image(self):
        if self.current_image is None:
            ctk_messagebox(title="Error", message="Please select an image first.")
            return
        save_image_via_dialog(self.current_image)

    def reset_image(self):
        if self.current_image is None:
            ctk_messagebox(title="Error", message="No image to reset.")
            return
        self.add_to_undo_stack()
        self.current_image = self.original_image.copy()
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry("Reset to original")

    def undo_image(self):
        if self.undo_stack:
            self.redo_stack.append(self.current_image.copy())
            self.current_image = self.undo_stack.pop()
            self.show_image(self.current_image)
            self.preview_base_image = None
            self.add_history_entry("Undo")
        else:
            ctk_messagebox(title="Info", message="Nothing to undo.")

    def redo_image(self):
        if self.redo_stack:
            self.undo_stack.append(self.current_image.copy())
            self.current_image = self.redo_stack.pop()
            self.show_image(self.current_image)
            self.preview_base_image = None
            self.add_history_entry("Redo")
        else:
            ctk_messagebox(title="Info", message="Nothing to redo.")

    def add_to_undo_stack(self):
        self.undo_stack.append(self.current_image.copy())
        self.redo_stack.clear()

    # ── Display ───────────────────────────────────────────────────────────────

    def show_image(self, image):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            w, h = 700, 450

        image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)

        img_w, img_h = image_pil.size
        if self.display_mode.get() == "fit-width":
            scale = w / img_w
        else:  # fit-window (default)
            scale = min(w / img_w, h / img_h)
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        image_pil = image_pil.resize((new_w, new_h), Image.LANCZOS)

        image_tk = ImageTk.PhotoImage(image=image_pil)
        self.canvas.delete("all")
        self.canvas.create_image(w // 2, h // 2, anchor="center", image=image_tk)
        self.canvas.image_tk = image_tk

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.app.destroy()

    # ── Generic filter applier ────────────────────────────────────────────────

    def _apply(self, fn, label):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        result = fn(self.current_image)
        if result is None:
            self.undo_stack.pop()
            return
        self.current_image = result
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(label)

    # ── One-click filter commands ─────────────────────────────────────────────

    def adjust_brightness(self):  self._apply(adjust_brightness,  "Brightness (dialog)")
    def adjust_contrast(self):    self._apply(adjust_contrast,    "Contrast (dialog)")
    def adjust_saturation(self):  self._apply(adjust_saturation,  "Saturation (dialog)")
    def apply_glitch(self):       self._apply(apply_glitch,       "Glitch")
    def apply_blur(self):         self._apply(apply_blur,         "Blur (dialog)")
    def apply_sharpen(self):      self._apply(apply_sharpen,      "Sharpen")
    def apply_pixels(self):       self._apply(apply_pixels,       "Pixelate")
    def apply_invert(self):       self._apply(apply_invert,       "Invert")
    def apply_noise(self):        self._apply(apply_noise,        "Noise (dialog)")
    def apply_vignette(self):     self._apply(apply_vignette,     "Vignette")
    def apply_retro_filter(self): self._apply(apply_retro_filter, "Retro filter")
    def apply_pencil(self):       self._apply(apply_pencil,       "Pencil sketch")
    def apply_smart_enhance(self):self._apply(apply_smart_enhance,"Smart Enhance")

    # ── Slider apply (committed on mouse-release) ─────────────────────────────

    def apply_brightness_from_slider(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        factor = self.brightness_slider.get()
        self.current_image = adjust_brightness_with_factor(self.current_image, factor)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Brightness: {factor:.2f}")

    def apply_contrast_from_slider(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        factor = self.contrast_slider.get()
        self.current_image = adjust_contrast_with_factor(self.current_image, factor)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Contrast: {factor:.2f}")

    def apply_saturation_from_slider(self):
        if not check_image_loaded(self.current_image):
            return
        self.add_to_undo_stack()
        factor = self.saturation_slider.get()
        self.current_image = adjust_saturation_with_factor(self.current_image, factor)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Saturation: {factor:.2f}")

    def apply_blur_from_slider(self):
        if not check_image_loaded(self.current_image):
            return
        radius = self.blur_slider.get()
        if radius <= 0:
            return
        self.add_to_undo_stack()
        self.current_image = apply_blur_with_radius(self.current_image, radius)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Blur: {radius:.1f}px")

    def apply_noise_from_slider(self):
        if not check_image_loaded(self.current_image):
            return
        intensity = self.noise_slider.get()
        if intensity <= 0:
            return
        self.add_to_undo_stack()
        self.current_image = apply_noise_with_intensity(self.current_image, intensity)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Noise: {intensity:.2f}")

    # ── Live preview callbacks (brightness & contrast only) ───────────────────

    def on_brightness_change(self, value):
        if self.current_image is None:
            return
        if self.preview_base_image is None:
            self.preview_base_image = self.current_image.copy()
        self.show_image(adjust_brightness_with_factor(self.preview_base_image, float(value)))

    def on_contrast_change(self, value):
        if self.current_image is None:
            return
        if self.preview_base_image is None:
            self.preview_base_image = self.current_image.copy()
        self.show_image(adjust_contrast_with_factor(self.preview_base_image, float(value)))

    # ── History helpers ───────────────────────────────────────────────────────

    def add_history_entry(self, text: str):
        lbl = ctk.CTkLabel(self.history_frame, text=text, anchor="w",
                           font=("Arial", 11), text_color=self.TEXT_SEC)
        lbl.pack(fill="x", padx=5, pady=2)
        self.history_entries.append(lbl)

    def clear_history(self):
        for lbl in self.history_entries:
            lbl.destroy()
        self.history_entries = []

    # ── Recent files ──────────────────────────────────────────────────────────

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

    # ── Batch helpers ─────────────────────────────────────────────────────────

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

        input_folder  = self.batch_input_entry.get().strip()
        output_folder = self.batch_output_entry.get().strip()
        if not input_folder or not output_folder:
            ctk_messagebox(title="Error", message="Please choose both input and output folders.")
            return

        process_folder_basic(
            input_folder=input_folder,
            output_folder=output_folder,
            apply_retro=self.batch_retro_var.get(),
            apply_sharpen_flag=self.batch_sharpen_var.get(),
            blur_radius=self.batch_blur_slider.get() if self.batch_blur_var.get() else None,
        )
        ctk_messagebox(title="Batch complete", message="Finished processing images in the folder.")

    # ── Misc ──────────────────────────────────────────────────────────────────

    def open_tutorial(self):
        pass

    # ── Keyboard shortcuts ────────────────────────────────────────────────────

    def _bind_shortcuts(self):
        pairs = [
            ("<Command-o>", "<Control-o>", self.load_image),
            ("<Command-s>", "<Control-s>", self.save_image),
            ("<Command-z>", "<Control-z>", self.undo_image),
            ("<Command-r>", "<Control-r>", self.reset_image),
            ("<Command-b>", "<Control-b>", self.apply_blur),
            ("<Command-e>", "<Control-e>", self.apply_smart_enhance),
        ]
        for mac, win, fn in pairs:
            self.app.bind(mac, lambda e, f=fn: f())
            self.app.bind(win, lambda e, f=fn: f())

        self.app.bind("<Shift-Command-Z>", lambda e: self.redo_image())
        self.app.bind("<Control-y>",       lambda e: self.redo_image())
