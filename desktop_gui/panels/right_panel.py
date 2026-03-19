"""
gui/panels/right_panel.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Right panel: collapsible Basic Adjustments + Creative Filters cards.
Also owns all filter action methods and slider handlers.

To add a new filter:
  1. Import its function from processing.filters
  2. Add a one-liner command method below
  3. Add a row to the `filters` list in _build_creative_filters()
"""

from utils.imports import ctk
from utils.utils import check_image_loaded
from processing.ml import remove_background
from processing.filters import (
    adjust_brightness_with_factor,
    adjust_contrast_with_factor,
    adjust_saturation_with_factor,
    apply_blur_with_radius,
    apply_noise_with_intensity,
    adjust_brightness,
    adjust_contrast,
    adjust_saturation,
    apply_glitch,
    apply_blur,
    apply_sharpen,
    apply_pixels,
    apply_invert,
    apply_noise,
    apply_vignette,
    apply_retro_filter,
    apply_pencil,
    apply_smart_enhance,
)


class RightPanelMixin:
    """Builds the right panel and owns all filter/slider logic."""

    # ── Panel construction ────────────────────────────────────────────────────

    def _build_right_panel(self):
        ctk.CTkLabel(self.right_panel, text="Adjustments & Filters",
                     font=("Arial", 15, "bold"), text_color=self.TEXT
                     ).pack(anchor="w", pady=(4, 10))

        adj_content = self._collapsible_card(self.right_panel, "✦   Basic Adjustments")
        self._build_basic_adjustments(adj_content)

        filt_content = self._collapsible_card(self.right_panel, "▼   Creative Filters")
        self._build_creative_filters(filt_content)

        ai_content = self._collapsible_card(self.right_panel, "AI Features")
        self._build_ai_features(ai_content)

    def _collapsible_card(self, parent, title):
        """Return the content frame of a collapsible white card."""
        card = ctk.CTkFrame(parent, fg_color=self.CARD, corner_radius=12)
        card.pack(fill="x", pady=(0, 10))
        is_open = [True]

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=12)

        ctk.CTkLabel(hdr, text=title,
                     font=("Arial", 13, "bold"), text_color=self.TEXT).pack(side="left", anchor="center")

        toggle_btn = ctk.CTkButton(
            hdr, text="∧", width=28, height=28,
            fg_color="transparent", hover_color=self.BG,
            text_color=self.TEXT_MUTED, font=("Arial", 15, "bold"),
            corner_radius=6,
        )
        toggle_btn.pack(side="right", anchor="center")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=14, pady=(0, 14))

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
            ("⚡", "Glitch Effect",  self.cmd_glitch),
            ("✨", "Sharpen",        self.cmd_sharpen),
            ("⊙", "Invert Colors",  self.cmd_invert),
            ("◉", "Vignette",       self.cmd_vignette),
            ("▦", "Pixelate",       self.cmd_pixels),
            ("↻", "Retro Filter",   self.cmd_retro_filter),
            ("✏", "Pencil Sketch",  self.cmd_pencil),
            ("⚙", "Smart Enhance",  self.cmd_smart_enhance),
        ]
        for icon, name, cmd in filters:
            ctk.CTkButton(
                parent, text=f"{icon}   {name}", command=cmd,
                fg_color=self.CARD, hover_color=self.BG,
                text_color=self.TEXT_SEC,
                border_width=1, border_color=self.BORDER,
                corner_radius=8, height=36, anchor="w",
            ).pack(fill="x", pady=(0, 6))

    def _build_ai_features(self, parent):
        self._ai_status = ctk.CTkLabel(
            parent, text="", font=("Arial", 11),
            text_color=self.TEXT_MUTED,
        )
        self._ai_status.pack(anchor="w", pady=(0, 4))

        self._ai_buttons = []

        features = [
            ("Remove Background", self.cmd_remove_background),
        ]
        for name, cmd in features:
            btn = ctk.CTkButton(
                parent, text=name, command=cmd,
                fg_color=self.ACCENT, hover_color="#6D28D9",
                text_color="white",
                corner_radius=8, height=36, anchor="w",
            )
            btn.pack(fill="x", pady=(0, 6))
            self._ai_buttons.append(btn)

    # ── One-click filter commands ─────────────────────────────────────────────

    def cmd_remove_background(self):
        def on_start():
            self._ai_status.configure(text="Processing...")
            for b in self._ai_buttons:
                b.configure(state="disabled")

        def on_done():
            self._ai_status.configure(text="")
            for b in self._ai_buttons:
                b.configure(state="normal")

        self._apply_ml(remove_background, "Remove Background",
                       on_start=on_start, on_done=on_done)

    def cmd_adjust_brightness(self): self._apply(adjust_brightness,  "Brightness (dialog)")
    def cmd_adjust_contrast(self):   self._apply(adjust_contrast,    "Contrast (dialog)")
    def cmd_adjust_saturation(self): self._apply(adjust_saturation,  "Saturation (dialog)")
    def cmd_glitch(self):            self._apply(apply_glitch,       "Glitch")
    def cmd_blur(self):              self._apply(apply_blur,         "Blur (dialog)")
    def cmd_sharpen(self):           self._apply(apply_sharpen,      "Sharpen")
    def cmd_pixels(self):            self._apply(apply_pixels,       "Pixelate")
    def cmd_invert(self):            self._apply(apply_invert,       "Invert")
    def cmd_noise(self):             self._apply(apply_noise,        "Noise (dialog)")
    def cmd_vignette(self):          self._apply(apply_vignette,     "Vignette")
    def cmd_retro_filter(self):      self._apply(apply_retro_filter, "Retro filter")
    def cmd_pencil(self):            self._apply(apply_pencil,       "Pencil sketch")
    def cmd_smart_enhance(self):     self._apply(apply_smart_enhance,"Smart Enhance")

    # ── Slider apply (committed on mouse-release) ─────────────────────────────

    def apply_brightness_from_slider(self):
        if not check_image_loaded(self.current_image, self.error_dialogs_enabled):
            return
        self.add_to_undo_stack()
        factor = self.brightness_slider.get()
        self.current_image = adjust_brightness_with_factor(self.current_image, factor)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Brightness: {factor:.2f}")

    def apply_contrast_from_slider(self):
        if not check_image_loaded(self.current_image, self.error_dialogs_enabled):
            return
        self.add_to_undo_stack()
        factor = self.contrast_slider.get()
        self.current_image = adjust_contrast_with_factor(self.current_image, factor)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Contrast: {factor:.2f}")

    def apply_saturation_from_slider(self):
        if not check_image_loaded(self.current_image, self.error_dialogs_enabled):
            return
        self.add_to_undo_stack()
        factor = self.saturation_slider.get()
        self.current_image = adjust_saturation_with_factor(self.current_image, factor)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Saturation: {factor:.2f}")

    def apply_blur_from_slider(self):
        if not check_image_loaded(self.current_image, self.error_dialogs_enabled):
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
        if not check_image_loaded(self.current_image, self.error_dialogs_enabled):
            return
        intensity = self.noise_slider.get()
        if intensity <= 0:
            return
        self.add_to_undo_stack()
        self.current_image = apply_noise_with_intensity(self.current_image, intensity)
        self.show_image(self.current_image)
        self.preview_base_image = None
        self.add_history_entry(f"Noise: {intensity:.2f}")

    # ── Live preview callbacks (brightness & contrast) ────────────────────────

    def on_brightness_change(self, value):
        if self.current_image is None:
            return
        if self.preview_base_image is None:
            self.preview_base_image = self.current_image.copy()
        self.show_image(
            adjust_brightness_with_factor(self.preview_base_image, float(value))
        )

    def on_contrast_change(self, value):
        if self.current_image is None:
            return
        if self.preview_base_image is None:
            self.preview_base_image = self.current_image.copy()
        self.show_image(
            adjust_contrast_with_factor(self.preview_base_image, float(value))
        )
