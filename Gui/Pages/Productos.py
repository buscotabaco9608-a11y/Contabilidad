import tkinter as tk 
from tkinter import ttk
from Gui.Pages.Ventas_Tabs.precios_tab import PreciosTab
from Core.ventas_backend import VentasBackend
from Gui.Pages.Styles.ventas_styles import VentasStyles

class ProductosFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.backend = VentasBackend()
        self.styles = VentasStyles()
        self.setup_ui()

        self.precios_tab = PreciosTab(self.notebook, self.backend)
        self.notebook.add(self.precios_tab, text="Precios de Venta")

    def setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)