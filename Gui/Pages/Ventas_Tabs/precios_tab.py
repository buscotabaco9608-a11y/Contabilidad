import tkinter as tk
from tkinter import ttk, messagebox
from Core.ventas_backend import VentasBackend

class PreciosTab(ttk.Frame):
    tab_name = "Precios"

    def __init__(self, parent, backend: VentasBackend):
        super().__init__(parent)
        self.backend = backend
        self.editing_entry = None
        self.setup_ui()
        self.load_precios()

    def setup_ui(self):
        precios_frame = ttk.Frame(self)
        precios_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(precios_frame, text="Precios de venta de Productos", font=("Segoe UI", 14, "bold")).pack(pady=5)

        columns = ("Productos", "Precio Costo", "Precio Venta", "Ganancia", "% Gan.")
        self.column_ids = columns
        self.precios_tree = ttk.Treeview(precios_frame, columns=columns, show="headings", height=12, style="Modern.Treeview")
        for c in columns:
            self.precios_tree.heading(c, text=c)
        self.precios_tree.column("Productos", width=220)
        self.precios_tree.column("Precio Costo", width=100, anchor=tk.E)
        self.precios_tree.column("Precio Venta", width=120, anchor=tk.E)
        self.precios_tree.column("Ganancia", width=100, anchor=tk.E)
        self.precios_tree.column("% Gan.", width=80, anchor=tk.E)
        self.precios_tree.pack(fill=tk.BOTH, expand=True)

        # Bind double click to start editing Precio Venta cell
        self.precios_tree.bind("<Double-1>", self.on_double_click)

        #boton para refrescar 
        refresh_btn = tk.Button(self, text="Actualizar", command=self.load_precios)
        refresh_btn.pack(pady=5)
        
    def load_precios(self):
        try:
            productos = self.backend.get_productos_con_costo()
            # Clear
            for i in self.precios_tree.get_children():
                self.precios_tree.delete(i)
            for p in productos:
                pid = p.get("id")
                costo = p.get("costo_unitario", 0.0)
                venta = p.get("precio_venta", 0.0) or 0.0
                gan = p.get("ganancia_unitaria", 0.0)
                pct = p.get("ganancia_pct", None)
                pct_display = f"{pct:.2f}%" if pct is not None else "-"
                # Use product id as iid so we can retrieve it later
                self.precios_tree.insert("", tk.END, iid=str(pid), values=(p.get("nombre"), f"${costo:.2f}", f"${venta:.2f}", f"${gan:.2f}", pct_display))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los precios: {e}")

    def _start_edit_cell(self, item_id, col_name, bbox):
        # Remove previous editing entry if any
        if self.editing_entry:
            try:
                self.editing_entry.destroy()
            except Exception:
                pass
            self.editing_entry = None

        # Get current value and strip $ if present
        cur_values = self.precios_tree.item(item_id, "values")
        # Map column index
        col_index = self.column_ids.index(col_name)
        cur_text = cur_values[col_index] if col_index < len(cur_values) else ""
        if isinstance(cur_text, str) and cur_text.startswith("$"):
            cur_text = cur_text[1:].strip()
        # Create entry over the tree cell
        x, y, width, height = bbox
        entry = tk.Entry(self.precios_tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, cur_text)
        entry.focus_set()

        def finish_edit(event=None):
            new_text = entry.get().strip()
            try:
                new_price = float(new_text) if new_text != "" else 0.0
            except Exception:
                messagebox.showwarning("Valor inválido", "Ingresa un número válido para precio")
                entry.focus_set()
                return
            # save to DB via backend
            try:
                self.backend.set_precio_venta(int(item_id), new_price)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el precio: {e}")
                entry.destroy()
                self.editing_entry = None
                return
            # update tree display
            vals = list(self.precios_tree.item(item_id, "values"))
            # precio venta is column "Precio Venta"
            try:
                col_idx = self.column_ids.index("Precio Venta")
                vals[col_idx] = f"${new_price:.2f}"
                self.precios_tree.item(item_id, values=vals)
            except Exception:
                pass
            # notify other tabs that price changed
            try:
                # generate virtual event on the notebook (parent) so RegistrarVentaTab can reload
                if hasattr(self.master, "event_generate"):
                    self.master.event_generate("<<PrecioActualizado>>")
            except Exception:
                pass
            entry.destroy()
            self.editing_entry = None

        entry.bind("<Return>", finish_edit)
        entry.bind("<FocusOut>", finish_edit)
        self.editing_entry = entry

    def on_double_click(self, event):
        region = self.precios_tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        col = self.precios_tree.identify_column(event.x)  # e.g., '#3'
        # map to column name
        col_index = int(col.replace("#", "")) - 1
        if col_index < 0 or col_index >= len(self.column_ids):
            return
        col_name = self.column_ids[col_index]
        # Only allow editing the "Precio Venta" column
        if col_name != "Precio Venta":
            return
        rowid = self.precios_tree.identify_row(event.y)
        if not rowid:
            return
        bbox = self.precios_tree.bbox(rowid, column=col)
        if not bbox:
            return
        # bbox returns (x, y, width, height)
        self._start_edit_cell(rowid, col_name, bbox)

