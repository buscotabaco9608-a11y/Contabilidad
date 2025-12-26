import tkinter as tk 
from tkinter import ttk, messagebox
from Gui.Pages.Styles.recetas_style import RecetasStyles
from Core.recetas_backend import RecetasBackend

class RecetasFrame(ttk.Frame):
    def __init__(self):
        super().__init__(self)
        self.styles = RecetasStyles()
        self.setup_ui()
