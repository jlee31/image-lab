"""
gui/panels/settings_tab.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Settings tab: notification toggles, display mode, TTS placeholder.
"""

import customtkinter as ctk


class SettingsTabMixin:
    """Builds the Settings tab."""

    def _create_settings_tab(self):
        tab = self.tabview.tab(self.TAB_SETTINGS)
        tab.configure(fg_color=self.BG)

        card = ctk.CTkFrame(tab, fg_color=self.CARD, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        frame = ctk.CTkFrame(card, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Notifications
        ctk.CTkLabel(frame, text="Notifications",
                     font=("Arial", 14, "bold"), text_color=self.TEXT
                     ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        ctk.CTkCheckBox(frame, text="Show success popups (e.g., after save/apply)",
                        variable=self.success_popups_enabled
                        ).grid(row=1, column=0, sticky="w", pady=2)
        ctk.CTkCheckBox(frame, text="Show error dialogs",
                        variable=self.error_dialogs_enabled
                        ).grid(row=2, column=0, sticky="w", pady=2)

        # Display mode
        ctk.CTkLabel(frame, text="Display",
                     font=("Arial", 14, "bold"), text_color=self.TEXT
                     ).grid(row=3, column=0, sticky="w", pady=(20, 5))
        ctk.CTkRadioButton(frame, text="Fit to width",
                           variable=self.display_mode, value="fit-width"
                           ).grid(row=4, column=0, sticky="w", pady=2)
        ctk.CTkRadioButton(frame, text="Fit to window",
                           variable=self.display_mode, value="fit-window"
                           ).grid(row=5, column=0, sticky="w", pady=2)

        # TTS placeholder
        ctk.CTkLabel(frame, text="TTS / Sound (future)",
                     font=("Arial", 14, "bold"), text_color=self.TEXT
                     ).grid(row=6, column=0, sticky="w", pady=(20, 5))
        ctk.CTkCheckBox(frame, text="Enable spoken feedback (planned)",
                        variable=self.tts_enabled, state="disabled"
                        ).grid(row=7, column=0, sticky="w", pady=2)
