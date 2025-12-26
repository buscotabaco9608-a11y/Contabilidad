"""
Página de Resúmenes con tabs de Inventario y Contabilidad
"""

import tkinter as tk
from tkinter import ttk
from Gui.Pages.ResumenesTabs. inventario_tab import InventarioTab
from Gui.Pages.ResumenesTabs.contabilidad_tab import ContabilidadTab
from Core.inventario_backend import InventarioBackend
from Core.logger import setup_logger


class ResumenesFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = setup_logger()
        self.backend = InventarioBackend()
        self.setup_ui()
        self.logger.info("ResumenesFrame initialized")

    def setup_ui(self):
        """Configuración de UI para la pestaña Resúmenes"""
        
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ===== HEADER =====
        header = tk.Frame(main, bg="#0dcaf0", height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="📊 Resúmenes Financieros",
            font=("Segoe UI", 24, "bold"),
            bg="#0dcaf0",
            fg="white",
            padx=10,
            pady=10
        )
        title.pack(side=tk.LEFT, fill=tk. BOTH, expand=True)
        
        # ===== TABS/NOTEBOOK =====
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab:  Inventario
        self.inv_tab = InventarioTab(self.notebook, self.backend)
        self.notebook.add(self.inv_tab, text="📦 Inventario")
        
        # Tab: Contabilidad (NUEVO)
        self.contabilidad_tab = ContabilidadTab(self.notebook, self.backend)
        self.notebook.add(self.contabilidad_tab, text="💰 Contabilidad")