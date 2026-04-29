"""
gui/panels/sidebar.py
~~~~~~~~~~~~~~~~~~~~~
Left sidebar: Quick Actions, History buttons, View History toggle.
"""

import customtkinter as ctk


class SidebarMixin:
    """Builds and manages the left sidebar panel."""

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

        self._sb_btn(sb, "📖   Tutorial",     self.open_tutorial,   ghost=True)
        self._sb_btn(sb, "🕐   View History", self._toggle_history, ghost=True)

        # Edit-history log — hidden until the user clicks View History
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

    def add_history_entry(self, text: str):
        lbl = ctk.CTkLabel(self.history_frame, text=text, anchor="w",
                           font=("Arial", 11), text_color=self.TEXT_SEC)
        lbl.pack(fill="x", padx=5, pady=2)
        self.history_entries.append(lbl)

    def clear_history(self):
        for lbl in self.history_entries:
            lbl.destroy()
        self.history_entries = []
