try:
    import tkinter as tk
    import customtkinter as ctk
    from tkinter import filedialog, simpledialog, messagebox, ttk
    from PIL import ImageTk
except ImportError:
    tk = ctk = filedialog = simpledialog = messagebox = ttk = ImageTk = None
