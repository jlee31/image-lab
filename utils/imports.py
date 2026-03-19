import cv2 as cv
import numpy as np
from PIL import Image, ImageTk, ImageEnhance, ImageFilter

# GUI imports — only available when running the desktop app, not the API server
try:
    import tkinter as tk
    import customtkinter as ctk
    from tkinter import filedialog, simpledialog, messagebox, ttk
except ImportError:
    pass
