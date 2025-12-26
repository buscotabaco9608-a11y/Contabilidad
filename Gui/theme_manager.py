import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """Manages application themes and styling."""
    
    def __init__(self):
        self.current_theme = "default"
        self.themes = {}
    
    def setup_labelframe(self):
        """Setup labelframe with correct ttk widget."""
        root = tk.Tk()
        # Changed from ttk.LabelFrame to ttk.Labelframe
        frame = ttk.Labelframe(root, text="Example")
        frame.pack()
        return frame
