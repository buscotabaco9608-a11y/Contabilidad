import tkinter as tk
from tkinter import ttk
from decimal import Decimal
from Core.inventario_backend import InventarioBackend

class InventarioTab(ttk.Frame):
    tab_name = "Inventario"
    
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend
        self.display_units = {}
        self.available_units = ['gr', 'Kg', 'Lb', 'Oz', 'L', 'ml'] # unidades comunes
        self.setup_ui()

    def setup_ui(self):
        # Frame Inventario
        inv_frame = ttk.Frame(self)
        inv_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        ttk.Label(inv_frame, text="Materias Primas en Inventario", font=("Arial", 14)).pack(pady=5)

        # Treeview para inventario
        columns = ("Producto", "Cantidad", "Unidad", "Costo Promedio", "Total Precio")
        self.inv_tree = ttk.Treeview(inv_frame, columns=columns, show="headings", height=10)
        self.inv_tree.heading("Producto", text="Producto")
        self.inv_tree.heading("Cantidad", text="Cantidad")
        self.inv_tree.heading("Unidad", text="Unidad")
        self.inv_tree.heading("Costo Promedio", text="Costo Promedio")
        self.inv_tree.heading("Total Precio", text="Total Precio")
        self.inv_tree.column("Producto", width=150)
        self.inv_tree.column("Cantidad", width=100)
        self.inv_tree.column("Unidad", width=100)
        self.inv_tree.column("Costo Promedio", width=100)
        self.inv_tree.column("Total Precio", width=100)
        self.inv_tree.pack(fill=tk.BOTH, expand=True)

        # Doble click para seleccion de unidades
        self.inv_tree.bind("<Double-1>", self.on_tree_double_click)

        #Scrollbar
        scrollbar = ttk.Scrollbar(inv_frame, orient=tk.VERTICAL, command=self.inv_tree.yview)
        self.inv_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Total invertido
        total_frame = tk.Frame(self)
        total_frame.pack(pady=10, padx=10, fill=tk.X)

        self.total_label = tk.Label(total_frame, text="Total invertido: $0.00", font=("Arial", 12, "bold"))
        self.total_label.pack()

        # Boton para refrescar 
        refresh_btn = tk.Button(self, text="Actualizar", command=self.load_inventario)
        refresh_btn.pack(pady=5)

        self.load_inventario()

    def load_inventario(self):
        # Limpiar inventario
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        # --- CHANGE THIS LINE ---
        # obtener datos del backend usando el nuevo método
        inventario_data = self.backend.get_inventario_para_resumen()
        
        total_invertido = 0
        for item in inventario_data:
            # The new method already prepares the data for display
            self.inv_tree.insert("", tk.END, values=(
                item['producto'],
                item['cantidad_display'], # e.g., "0.80"
                item['unidad_display'],    # e.g., "kg"
                item['costo_promedio_display'], # e.g., "$0.1750"
                f"${item['total_valor']:.2f}"
            ))
            total_invertido += item['total_valor']
            
        self.total_label.config(text=f"Total invertido: ${total_invertido:.2f}")

    def on_tree_double_click(self, event):
        # Placeholder for future implementation
        pass
