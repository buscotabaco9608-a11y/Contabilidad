import tkinter as tk
from tkinter import ttk, messagebox
from Gui.Pages.Styles.ventas_styles import VentasStyles
from Core.ventas_backend import VentasBackend
from Gui.Pages.Ventas_Tabs.clientes_tab import ClientesTab
from Gui.Pages.Ventas_Tabs.history_tab import HistorialTab
# from Gui.Pages.Ventas_Tabs.precios_tab import PreciosTab
from Gui.Pages.Ventas_Tabs.ventas_registro_tab import RegistrarVentaTab
from Core.logger import setup_logger

class VentasFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.backend = VentasBackend()
        self.logger = setup_logger()
        self.styles = VentasStyles()
        self.setup_ui()


        # self.precios_tab = PreciosTab(self.notebook, self.backend)
        # self.notebook.add(self.precios_tab, text="Precios de Venta")

        self.clientes_tab = ClientesTab(self.notebook, self.backend)
        self.notebook.add(self.clientes_tab, text="Clientes")

        self.registrar_tab = RegistrarVentaTab(self.notebook, self.backend)
        self.notebook.add(self.registrar_tab, text="Registrar Venta")

        self.historial_tab = HistorialTab(self.notebook, self.backend)
        self.notebook.add(self.historial_tab, text="Historial de Ventas")

    def setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)





