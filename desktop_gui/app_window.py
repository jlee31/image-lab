import threading
import numpy as np
import tkinter as tk
from tkinter import messagebox
import cv2 as cv
import customtkinter as ctk
from utils.gui_utils import load_image_via_dialog, save_image_via_dialog, check_image_loaded
from utils.customMessageBox import ctk_messagebox
from .panels import (
    SidebarMixin,
    CanvasMixin,
    RightPanelMixin,
    BatchTabMixin,
    SettingsTabMixin,
)


class AppWindow(SidebarMixin, CanvasMixin, RightPanelMixin, BatchTabMixin, SettingsTabMixin):
    # ── Colour palette ────────────────────────────────────────────────────────
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

    # ── Tab name constants ─────────────────────────────────────────────────────
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

        # ── Image state ───────────────────────────────────────────────────────
        self.original_image     = None
        self.current_image      = None
        self.undo_stack         = []
        self.redo_stack         = []
        self.preview_base_image = None
        self.recent_files       = []
        self.history_entries    = []
        self._history_visible   = False

        # ── Settings vars (created here so panels can reference them) ─────────
        self.success_popups_enabled = tk.BooleanVar(value=True)
        self.error_dialogs_enabled  = tk.BooleanVar(value=True)
        self.display_mode        = tk.StringVar(value="fit-window")
        self.tts_enabled         = tk.BooleanVar(value=False)

        # Re-render when the user changes display mode in Settings
        self.display_mode.trace_add("write", lambda *_: self._on_display_mode_change())

        # ── Build UI ──────────────────────────────────────────────────────────
        self._create_header()
        self._create_tabs()
        self._create_photo_editor_tab()
        self._create_batch_tab()
        self._create_settings_tab()
        self._bind_shortcuts()

        # Re-render the canvas when the user switches back to the Editor tab
        # (e.g. after changing display mode in Settings).
        self.tabview.configure(command=self._on_tab_change)

        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app.mainloop()

    # ── Header ────────────────────────────────────────────────────────────────

    def _create_header(self):
        header = ctk.CTkFrame(self.app, fg_color=self.CARD, corner_radius=0)
        header.pack(fill="x", side="top")

        icon_bg = ctk.CTkFrame(header, fg_color=self.ACCENT, width=44, height=44, corner_radius=10)
        icon_bg.pack(side="left", padx=(20, 10), pady=16)
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="🖼", font=("Arial", 22), text_color="white").pack(expand=True)

        text_col = ctk.CTkFrame(header, fg_color="transparent")
        text_col.pack(side="left", pady=16)
        tk.Label(text_col, text="Image Lab",
                 font=("Arial", 19, "bold"), fg=self.TEXT, bg=self.CARD,
                 borderwidth=0).pack(anchor="w", pady=(0, 3))
        tk.Label(text_col, text="Professional Photo Editing Suite",
                 font=("Arial", 11), fg=self.TEXT_MUTED, bg=self.CARD,
                 borderwidth=0).pack(anchor="w", pady=(0, 3))

        ctk.CTkFrame(self.app, fg_color=self.BORDER, height=1, corner_radius=0).pack(fill="x")

    # ── Tab bar ───────────────────────────────────────────────────────────────

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

    # ── Photo Editor tab layout ───────────────────────────────────────────────

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

        # Delegate to mixins
        self._build_left_sidebar()   # SidebarMixin
        self._build_canvas_area()    # CanvasMixin
        self._build_right_panel()    # RightPanelMixin

    # ── Image operations ──────────────────────────────────────────────────────

    def load_image(self):
        file_path = load_image_via_dialog()
        if file_path:
            self.original_image = cv.imread(filename=file_path)
            self.current_image = self.original_image.copy()
            self.preview_base_image = None
            self._show_canvas()           # CanvasMixin: swap in the canvas
            self.show_image(self.current_image)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.clear_history()
            self._add_recent_file(file_path)

    def save_image(self):
        if self.current_image is None:
            ctk_messagebox(title="Error", message="Please select an image first.")
            return
        save_image_via_dialog(self.current_image, self.success_popups_enabled, self.error_dialogs_enabled)

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

    # ── Generic filter applier (used by all cmd_* methods in RightPanelMixin) ─

    def _apply(self, fn, label):
        if not check_image_loaded(self.current_image, self.error_dialogs_enabled):
            return
        self.add_to_undo_stack()

        # If the current image has an alpha channel, apply the filter only to
        # the BGR channels and then reattach the alpha.
        if self.current_image.ndim == 3 and self.current_image.shape[2] == 4:
            alpha = self.current_image[:, :, 3:4]
            result = fn(self.current_image[:, :, :3])
            if result is None:
                self.undo_stack.pop()
                return
            result = np.concatenate([result, alpha], axis=2)
        else:
            result = fn(self.current_image)
            if result is None:
                self.undo_stack.pop()
                return

        self.current_image = result
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(label)

    def _apply_ml(self, fn, label, on_start=None, on_done=None):
        """Run an ML filter in a background thread to keep the UI responsive."""
        if not check_image_loaded(self.current_image, self.error_dialogs_enabled):
            return
        self.add_to_undo_stack()
        image_copy = self.current_image.copy()

        if on_start:
            on_start()

        def _run():
            try:
                result = fn(image_copy)
            except Exception as e:
                msg = str(e)
                self.app.after(0, lambda: self._ml_error(msg, on_done))
                return
            self.app.after(0, lambda: self._ml_finish(result, label, on_done))

        threading.Thread(target=_run, daemon=True).start()

    def _ml_finish(self, result, label, on_done=None):
        if result is None:
            self.undo_stack.pop()
        else:
            self.current_image = result
            self.show_image(self.current_image)
            self.preview_base_image = None
            self.add_history_entry(label)
        if on_done:
            on_done()

    def _ml_error(self, message, on_done=None):
        self.undo_stack.pop()
        ctk_messagebox(title="Error", message=message)
        if on_done:
            on_done()

    # ── Misc ──────────────────────────────────────────────────────────────────

    def _on_tab_change(self):
        tab_name = self.tabview.get()
        if tab_name == self.TAB_EDITOR and self.current_image is not None:
            self.app.after(50, lambda: self.show_image(self.current_image))

    def open_tutorial(self):
        pass

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.app.destroy()

    # ── Keyboard shortcuts ─────────────────────────────────────────────────────

    def _bind_shortcuts(self):
        pairs = [
            ("<Command-o>", "<Control-o>", self.load_image),
            ("<Command-s>", "<Control-s>", self.save_image),
            ("<Command-z>", "<Control-z>", self.undo_image),
            ("<Command-r>", "<Control-r>", self.reset_image),
            ("<Command-b>", "<Control-b>", self.cmd_blur),
            ("<Command-e>", "<Control-e>", self.cmd_smart_enhance),
        ]
        for mac, win, fn in pairs:
            self.app.bind(mac, lambda e, f=fn: f())
            self.app.bind(win, lambda e, f=fn: f())

        self.app.bind("<Shift-Command-Z>", lambda e: self.redo_image())
        self.app.bind("<Control-y>",       lambda e: self.redo_image())
