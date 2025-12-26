import tkinter as tk
from tkinter import ttk, messagebox
from Core.ventas_backend import VentasBackend

class HistorialTab(ttk.Frame):
    tab_name = "Historial"
    
    def __init__(self, parent, backend: VentasBackend):
        super().__init__(parent)
        self.backend = backend
        self.setup_ui()
        self.load_historial()

    def setup_ui(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        cols = ("Fecha", "Cliente", "Producto", "Cantidad", "Precio/u", "Total")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=15, style="Modern.Treeview")
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.column("Fecha", width=140)
        self.tree.column("Cliente", width=160)
        self.tree.column("Producto", width=160)
        self.tree.column("Cantidad", width=80, anchor=tk.E)
        self.tree.column("Precio/u", width=100, anchor=tk.E)
        self.tree.column("Total", width=100, anchor=tk.E)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def load_historial(self):
        try:
            rows = self.backend.get_historial_ventas()
            for i in self.tree.get_children():
                self.tree.delete(i)
            for r in rows:
                self.tree.insert("", tk.END, values=(
                    str(r.get("fecha_venta")),
                    r.get("cliente"),
                    r.get("producto"),
                    r.get("cantidad_vendida"),
                    f"${float(r.get('precio_unitario_venta') or 0):.2f}",
                    f"${float(r.get('total_venta') or 0):.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar historial: {e}")