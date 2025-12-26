import tkinter as tk
from tkinter import ttk, messagebox
from Core.ventas_backend import VentasBackend
from Core.logger import setup_logger


class RegistrarVentaTab(ttk.Frame):
    """Tab para registrar nuevas ventas con diseño moderno en tkinter puro."""
    
    tab_name = "Registrar Venta"

    def __init__(self, parent, backend:   VentasBackend):
        super().__init__(parent)
        self.backend = backend
        self.logger = setup_logger()
        
        # Mapeos de productos y clientes
        self.product_map = {}
        self.client_name_to_id = {}
        self.product_display_list = []
        self.display_to_name = {}
        
        # Items en la tabla
        self.item_rows = []
        self.next_item_id = 1
        
        self.selected_client_id = None
        self.selected_client_name = None
        
        self.setup_ui()
        self.load_products()
        self.load_clients()
        self.logger.info("RegistrarVentaTab initialized")

    def setup_ui(self):
        """Configurar la interfaz de usuario."""
        
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ===== HEADER =====
        header_frame = tk.Frame(main, bg="#198754", height=70)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="➕ Registrar Nueva Venta",
            font=("Segoe UI", 20, "bold"),
            bg="#198754",
            fg="white",
            padx=10,
            pady=10
        )
        title.pack(side=tk.LEFT, fill=tk. BOTH, expand=True)
        
        # ===== CONTENEDOR PRINCIPAL (2 COLUMNAS) =====
        content = ttk.Frame(main)
        content.pack(fill=tk.BOTH, expand=True)
        
        # ===== COLUMNA IZQUIERDA:  Tabla de Productos =====
        left_panel = tk.LabelFrame(
            content,
            text="📦 Productos a Vender",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=10,
            pady=10,
            fg="#0078d4"
        )
        left_panel.pack(side=tk.LEFT, fill=tk. BOTH, expand=True, padx=(0, 10))
        
        # Botón para agregar producto
        add_product_btn = tk.Button(
            left_panel,
            text="➕ Agregar Producto",
            command=self.add_item,
            bg="#0078d4",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        add_product_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para tabla con scrollbar
        tree_frame = ttk.Frame(left_panel)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tabla de productos (Treeview)
        columns = ("ID", "Producto", "Cantidad", "Precio Unit.", "Subtotal", "Acción")
        self.products_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=12
        )
        
        # Configurar encabezados
        self.products_tree.heading("ID", text="ID")
        self.products_tree.heading("Producto", text="📦 Producto")
        self.products_tree.heading("Cantidad", text="Cantidad")
        self.products_tree.heading("Precio Unit.", text="Precio Unit.")
        self.products_tree.heading("Subtotal", text="Subtotal")
        self.products_tree.heading("Acción", text="Acción")
        
        # Configurar anchos
        self.products_tree.column("ID", width=30, anchor=tk.CENTER)
        self.products_tree.column("Producto", width=150)
        self.products_tree. column("Cantidad", width=80, anchor=tk.CENTER)
        self.products_tree.column("Precio Unit.", width=90, anchor=tk.E)
        self.products_tree.column("Subtotal", width=90, anchor=tk.E)
        self.products_tree.column("Acción", width=70, anchor=tk.CENTER)
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk. Scrollbar(
            tree_frame,
            orient=tk.VERTICAL,
            command=self.products_tree. yview
        )
        self.products_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk. RIGHT, fill=tk.Y)
        
        # Bind eventos
        self.products_tree. bind("<Double-1>", self.on_tree_double_click)
        self.products_tree.bind("<Button-3>", self.on_tree_right_click)
        
        # Resumen
        summary_frame = tk. Frame(left_panel, bg="white")
        summary_frame.pack(fill=tk. X, pady=10)
        
        tk.Label(
            summary_frame,
            text="Subtotal:",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(side=tk.LEFT)
        
        self.subtotal_label = tk. Label(
            summary_frame,
            text="$0.00",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#0078d4"
        )
        self.subtotal_label.pack(side=tk.LEFT, padx=10)
        
        # ===== COLUMNA DERECHA: Clientes =====
        right_panel = tk.LabelFrame(
            content,
            text="👥 Seleccionar Cliente",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=10,
            pady=10,
            fg="#198754"
        )
        right_panel.pack(side=tk.RIGHT, fill=tk. BOTH, expand=True, padx=(10, 0))
        
        # Frame tabla clientes
        client_tree_frame = ttk.Frame(right_panel)
        client_tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tabla de clientes
        client_cols = ("Nombre", "Estado")
        self.clients_tree = ttk.Treeview(
            client_tree_frame,
            columns=client_cols,
            show="headings",
            height=12
        )
        
        self.clients_tree.heading("Nombre", text="👤 Nombre")
        self.clients_tree.heading("Estado", text="Estado")
        
        self.clients_tree.column("Nombre", width=180)
        self.clients_tree.column("Estado", width=80, anchor=tk.CENTER)
        
        self.clients_tree.pack(side=tk.LEFT, fill=tk. BOTH, expand=True)
        
        # Scrollbar clientes
        client_scrollbar = ttk. Scrollbar(
            client_tree_frame,
            orient=tk.VERTICAL,
            command=self.clients_tree.yview
        )
        self.clients_tree.configure(yscroll=client_scrollbar.set)
        client_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selección
        self.clients_tree.bind("<<TreeviewSelect>>", self.on_client_select)
        
        # Info cliente
        info_frame = tk. Frame(right_panel, bg="white")
        info_frame.pack(fill=tk. X, pady=10)
        
        tk.Label(
            info_frame,
            text="Cliente Seleccionado:",
            font=("Segoe UI", 9, "bold"),
            bg="white"
        ).pack(anchor="w")
        
        self. selected_client_label = tk. Label(
            info_frame,
            text="(Ninguno)",
            font=("Segoe UI", 10),
            bg="white",
            fg="#ffc107",
            padx=10
        )
        self.selected_client_label.pack(anchor="w")
        
        # ===== FOOTER:  Total y Botones =====
        footer = ttk.Frame(main)
        footer.pack(fill=tk.X, pady=(15, 0))
        
        # Total
        total_frame = tk.Frame(footer, bg="#198754", height=60)
        total_frame.pack(fill=tk.X, pady=(0, 10))
        total_frame.pack_propagate(False)
        
        tk. Label(
            total_frame,
            text="💰 TOTAL A PAGAR:",
            font=("Segoe UI", 12, "bold"),
            bg="#198754",
            fg="white",
            padx=10
        ).pack(side=tk.LEFT, pady=10)
        
        self. total_label = tk.Label(
            total_frame,
            text="$0.00",
            font=("Segoe UI", 16, "bold"),
            bg="#198754",
            fg="white",
            padx=15
        )
        self.total_label.pack(side=tk.LEFT)
        
        # Botones
        buttons_frame = tk.Frame(footer, bg="white")
        buttons_frame. pack(fill=tk.X)
        
        register_btn = tk.Button(
            buttons_frame,
            text="✅ Registrar Venta",
            command=self.submit_sale,
            bg="#198754",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        register_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            buttons_frame,
            text="🔄 Limpiar",
            command=self.clear_form,
            bg="#6c757d",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

    def load_products(self):
        """Cargar productos disponibles."""
        try:
            prods = self.backend.get_productos_con_costo()
            self.product_map. clear()
            self.product_display_list = []
            self.display_to_name = {}
            
            for p in prods:
                name = p.get("nombre", "")
                self.product_map[name] = p
                display = f"{name} — ${p.get('precio_venta', 0):.2f}"
                self.product_display_list.append(display)
                self.display_to_name[display] = name
            
            self.logger.info(f"Cargados {len(self.product_map)} productos")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar productos: {e}")
            self.logger.error(f"Error al cargar productos: {e}")

    def load_clients(self):
        """Cargar clientes activos."""
        try:
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            
            rows = self.backend.get_clientes_activos()
            self.client_name_to_id = {r["nombre"]: r["id"] for r in rows}
            
            for client in rows:
                self.clients_tree.insert(
                    "",
                    tk.END,
                    iid=str(client["id"]),
                    values=(client["nombre"], "✅ Activo")
                )
            
            self.logger.info(f"Cargados {len(rows)} clientes")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar clientes: {e}")
            self.logger. error(f"Error al cargar clientes: {e}")

    def on_client_select(self, event):
        """Manejar selección de cliente."""
        selection = self.clients_tree.selection()
        
        if selection:
            try:
                client_id = int(selection[0])
                self.selected_client_id = client_id
                
                for name, cid in self.client_name_to_id.items():
                    if cid == client_id:
                        self.selected_client_name = name
                        break
                
                self.selected_client_label.config(text=f"👤 {self.selected_client_name}")
                self.logger.info(f"Cliente seleccionado: {self.selected_client_name}")
                
            except Exception as e:
                self.logger.error(f"Error al seleccionar cliente: {e}")

    def add_item(self):
        """Agregar producto a la tabla."""
        
        if not self.product_display_list:
            messagebox. showwarning("Aviso", "No hay productos disponibles")
            return
        
        # Dialog
        dialog = tk.Toplevel(self)
        dialog.title("Agregar Producto")
        dialog.geometry("450x250")
        dialog.transient(self. winfo_toplevel())
        dialog.grab_set()
        dialog.resizable(False, False)
        
        main_frame = tk.Frame(dialog, bg="white")
        main_frame. pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Producto
        tk.Label(
            main_frame,
            text="📦 Producto:",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        product_combo = ttk.Combobox(
            main_frame,
            values=self.product_display_list,
            state="readonly",
            width=40
        )
        product_combo.pack(fill=tk.X, pady=(0, 15))
        product_combo.set(self.product_display_list[0] if self.product_display_list else "")
        
        # Cantidad
        tk.Label(
            main_frame,
            text="📊 Cantidad:",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        qty_entry = tk.Entry(
            main_frame,
            font=("Segoe UI", 10),
            width=40
        )
        qty_entry.insert(0, "1")
        qty_entry.pack(fill=tk.X, pady=(0, 20))
        qty_entry.focus()
        qty_entry.select_range(0, tk.END)
        
        def on_add():
            try:
                display = product_combo.get()
                if not display:
                    messagebox. showwarning("Aviso", "Selecciona un producto")
                    return
                
                prod_name = self.display_to_name.get(display)
                prod = self.product_map.get(prod_name)
                
                if not prod:
                    messagebox. showerror("Error", "Producto no encontrado")
                    return
                
                # ✅ CORREGIDO: Convertir a float primero, luego validar
                qty_str = qty_entry.get().strip()
                try:
                    qty_float = float(qty_str)
                    qty = int(qty_float)
                except ValueError:
                    messagebox. showerror("Error", "La cantidad debe ser un número")
                    return
                
                if qty <= 0:
                    messagebox.showwarning("Aviso", "La cantidad debe ser mayor a 0")
                    return
                
                # Agregar a tabla
                item_id = self.next_item_id
                self. next_item_id += 1
                
                unit_price = float(prod.get("precio_venta", 0) or 0)
                subtotal = unit_price * qty
                
                self.products_tree.insert(
                    "",
                    tk.END,
                    iid=str(item_id),
                    values=(
                        item_id,
                        prod_name,
                        qty,
                        f"${unit_price:.2f}",
                        f"${subtotal:.2f}",
                        "❌"
                    )
                )
                
                self.item_rows.append({
                    'item_id': item_id,
                    'product_id': prod. get('id'),
                    'product_name': prod_name,
                    'quantity':  qty,
                    'unit_price': unit_price
                })
                
                self. update_total()
                self.logger.info(f"Producto agregado: {prod_name} x {qty}")
                dialog.destroy()
                
            except Exception as e:
                self.logger.error(f"Error al agregar item: {e}")
                messagebox.showerror("Error", f"Error:  {str(e)}")
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            btn_frame,
            text="✅ Agregar",
            command=on_add,
            bg="#0078d4",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            relief=tk. FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=dialog.destroy,
            bg="#6c757d",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            relief=tk. FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        qty_entry.bind("<Return>", lambda e: on_add())

    def on_tree_double_click(self, event):
        """Editar cantidad con doble-click."""
        item = self.products_tree.selection()
        if not item:
            return
        
        item_id = item[0]
        row_data = next((r for r in self.item_rows if str(r['item_id']) == item_id), None)
        
        if not row_data: 
            return
        
        # Dialog editar
        dialog = tk. Toplevel(self)
        dialog.title(f"Editar:  {row_data['product_name']}")
        dialog.geometry("350x200")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.resizable(False, False)
        
        main_frame = tk.Frame(dialog, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(
            main_frame,
            text=f"📦 Producto: {row_data['product_name']}",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 15))
        
        tk.Label(
            main_frame,
            text="Nueva Cantidad:",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        qty_entry = tk.Entry(
            main_frame,
            font=("Segoe UI", 10),
            width=30
        )
        qty_entry.insert(0, str(row_data['quantity']))
        qty_entry.pack(fill=tk.X, pady=(0, 20))
        qty_entry.focus()
        qty_entry.selection_range(0, tk.END)
        
        def on_update():
            try:
                qty_str = qty_entry.get().strip()
                try:
                    qty_float = float(qty_str)
                    new_qty = int(qty_float)
                except ValueError:
                    messagebox.showerror("Error", "La cantidad debe ser un número")
                    return
                
                if new_qty <= 0:
                    messagebox. showwarning("Aviso", "La cantidad debe ser mayor a 0")
                    return
                
                row_data['quantity'] = new_qty
                new_subtotal = row_data['unit_price'] * new_qty
                
                self.products_tree.item(item_id, values=(
                    row_data['item_id'],
                    row_data['product_name'],
                    new_qty,
                    f"${row_data['unit_price']:.2f}",
                    f"${new_subtotal:.2f}",
                    "❌"
                ))
                
                self.update_total()
                dialog.destroy()
                self.logger.info(f"Cantidad actualizada: {row_data['product_name']} -> {new_qty}")
                
            except Exception as e:
                self.logger.error(f"Error al actualizar: {e}")
                messagebox.showerror("Error", f"Error: {str(e)}")
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk. Button(
            btn_frame,
            text="✅ Actualizar",
            command=on_update,
            bg="#198754",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=dialog.destroy,
            bg="#6c757d",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            relief=tk. FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        qty_entry.bind("<Return>", lambda e: on_update())

    def on_tree_right_click(self, event):
        """Menú contextual con click derecho."""
        item = self. products_tree.identify('item', event.x, event. y)
        
        if not item:
            return
        
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="✏️ Editar", command=lambda: self.on_tree_double_click(None))
        context_menu.add_separator()
        context_menu.add_command(
            label="❌ Eliminar",
            command=lambda: self.remove_item(int(item)),
            foreground="red"
        )
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def remove_item(self, item_id):
        """Eliminar producto."""
        
        if not messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            return
        
        self.item_rows = [r for r in self.item_rows if r['item_id'] != item_id]
        self.products_tree.delete(str(item_id))
        self.update_total()
        self.logger.info(f"Producto eliminado: ID {item_id}")

    def update_total(self):
        """Actualizar totales."""
        subtotal = sum(r['unit_price'] * r['quantity'] for r in self.item_rows)
        self.subtotal_label.config(text=f"${subtotal:.2f}")
        self.total_label.config(text=f"${subtotal:.2f}")

    def submit_sale(self):
        """Registrar venta."""
        
        if not self.selected_client_id:
            messagebox.showwarning("Aviso", "Selecciona un cliente")
            return
        
        if not self. item_rows:
            messagebox. showwarning("Aviso", "Agrega al menos un producto")
            return
        
        try:
            # Preparar items
            items = [
                {
                    'product_id': r['product_id'],
                    'quantity': r['quantity'],
                    'unit_price': r['unit_price']
                }
                for r in self.item_rows
            ]
            
            # Registrar en backend
            result = self.backend.crear_venta_multiple(self.selected_client_id, items)
            total = result. get('total', 0)
            
            messagebox.showinfo(
                "✅ Éxito",
                f"Venta registrada exitosamente\n\n"
                f"Cliente: {self.selected_client_name}\n"
                f"Total: ${total:.2f}"
            )
            
            self.clear_form()
            self.logger.info(f"Venta registrada - {self.selected_client_name}:  ${total:.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar:  {str(e)}")
            self.logger.error(f"Error al registrar venta: {e}")

    def clear_form(self):
        """Limpiar formulario."""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        for item in self.clients_tree.get_children():
            self.clients_tree.selection_remove(item)
        
        self.item_rows. clear()
        self.selected_client_id = None
        self.selected_client_name = None
        self.next_item_id = 1
        
        self.selected_client_label.config(text="(Ninguno)")
        self.subtotal_label.config(text="$0.00")
        self.total_label.config(text="$0.00")
        
        self.logger.info("Formulario limpiado")