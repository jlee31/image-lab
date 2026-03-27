"""
gui/panels/batch_tab.py
~~~~~~~~~~~~~~~~~~~~~~~
Batch Tools tab: folder selection, pipeline options, recent files list.
"""

from utils.imports import ctk, tk, filedialog
from utils.customMessageBox import ctk_messagebox


class BatchTabMixin:
    """Builds and manages the Batch Tools tab."""

    def _create_batch_tab(self):
        tab = self.tabview.tab(self.TAB_BATCH)
        tab.configure(fg_color=self.BG)

        card = ctk.CTkFrame(tab, fg_color=self.CARD, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        frame = ctk.CTkFrame(card, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Input / output folder rows
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

        # Pipeline options
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

        # Recent files
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

    # ── Folder pickers ────────────────────────────────────────────────────────

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

    # ── Processing ────────────────────────────────────────────────────────────

    def _run_batch_processing(self):
        from processing.batch import process_folder_basic

        input_folder  = self.batch_input_entry.get().strip()
        output_folder = self.batch_output_entry.get().strip()
        if not input_folder or not output_folder:
            ctk_messagebox(title="Error", message="Please choose both input and output folders.")
            return

        try:
            process_folder_basic(
                input_folder=input_folder,
                output_folder=output_folder,
                apply_retro=self.batch_retro_var.get(),
                apply_sharpen_flag=self.batch_sharpen_var.get(),
                blur_radius=self.batch_blur_slider.get() if self.batch_blur_var.get() else None,
            )
        except FileNotFoundError as e:
            ctk_messagebox(title="Error", message=str(e))
            return
        ctk_messagebox(title="Batch complete", message="Finished processing images in the folder.")

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
