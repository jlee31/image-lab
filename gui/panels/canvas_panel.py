"""
gui/panels/canvas_panel.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Centre canvas area: empty state frame and image display.
"""

import tkinter as tk
from utils.imports import cv, Image, ImageTk, ctk


class CanvasMixin:
    """Builds and manages the centre canvas area."""

    def _build_canvas_area(self):
        # ── Empty state (shown before any image is loaded) ──
        self._empty_frame = ctk.CTkFrame(self.canvas_frame, fg_color=self.CARD, corner_radius=0)
        self._empty_frame.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(self._empty_frame, fg_color="transparent")
        inner.place(relx=0.5, rely=0.45, anchor="center")

        circle = ctk.CTkFrame(inner, fg_color=self.ACCENT_LIGHT,
                              width=116, height=116, corner_radius=58)
        circle.pack()
        circle.pack_propagate(False)
        ctk.CTkLabel(circle, text="📷", font=("Arial", 44)).pack(expand=True)

        ctk.CTkLabel(inner, text="No Image Loaded",
                     font=("Arial", 17, "bold"), text_color=self.TEXT).pack(pady=(20, 0))
        ctk.CTkLabel(inner,
                     text="Upload an image to start editing with our\nprofessional tools",
                     font=("Arial", 11), text_color=self.TEXT_MUTED,
                     justify="center").pack(pady=(8, 20))
        ctk.CTkButton(inner, text="↑   Choose Image", command=self.load_image,
                      fg_color=self.PRIMARY, hover_color=self.PRIMARY_HOVER,
                      text_color="white", corner_radius=8,
                      height=40, width=160).pack()

        # ── Canvas (hidden until first image is loaded) ──
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.CARD, highlightthickness=0)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _on_canvas_resize(self, _event):
        if self.current_image is not None:
            self.show_image(self.current_image)

    def _show_canvas(self):
        """Swap the empty-state frame out and show the canvas."""
        self._empty_frame.pack_forget()
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)

    def _on_display_mode_change(self):
        if self.current_image is not None:
            # The canvas may be on a hidden tab, so schedule the re-render
            # for after the event loop has a chance to update geometry.
            self.app.after(50, lambda: self._deferred_show())

    def _deferred_show(self):
        if self.current_image is not None:
            self.show_image(self.current_image)

    def show_image(self, image):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            w, h = 700, 450

        if image.ndim == 3 and image.shape[2] == 4:
            # BGRA: composite over a checkerboard to show transparency
            rgba = image[:, :, [2, 1, 0, 3]]
            fg = Image.fromarray(rgba, "RGBA")
            checker = _make_checkerboard(fg.size)
            checker.paste(fg, mask=fg.split()[3])
            image_pil = checker.convert("RGB")
        else:
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
        self.canvas.image_tk = image_tk  # keep reference to prevent GC


def _make_checkerboard(size, tile=16):
    """Return a grey checkerboard PIL image of the given size."""
    import numpy as np
    w, h = size
    ys = np.arange(h) // tile
    xs = np.arange(w) // tile
    grid = (ys[:, None] + xs[None, :]) % 2  # 0 = light, 1 = dark
    arr = np.where(grid[:, :, None], 170, 220).astype(np.uint8)
    arr = np.broadcast_to(arr, (h, w, 3)).copy()
    return Image.fromarray(arr, "RGB")
