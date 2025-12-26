"""
Página de Producción - Gestión de subproductos y productos finales
"""

import tkinter as tk
from tkinter import ttk, messagebox
from Core.produccion_backend import ProduccionBackend
from Core.inventario_backend import InventarioBackend
from Core.logger import setup_logger


class ProduccionFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.backend = ProduccionBackend()
        self.inv_backend = InventarioBackend()
        self.logger = setup_logger()

        # Estado
        self.ingredientes_list = []
        self.selected_subproducto_id = None
        self.selected_subproducto_data = None
        self.subproductos_map = {}
        self.productos_finales_map = {}

        self.setup_ui()
        self.load_ingredient_combo()
        self.load_subproductos()
        self.load_productos_finales()
        self.logger.info("ProduccionFrame initialized")

    def setup_ui(self):
        """Configurar interfaz principal."""

        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ===== HEADER =====
        header = tk.Frame(main, bg="#ffc107", height=70)
        header.pack(fill=tk.X, pady=(0, 15))
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="⚙️ Gestión de Producción",
            font=("Segoe UI", 20, "bold"),
            bg="#ffc107",
            fg="white",
            padx=10,
            pady=10
        )
        title.pack(side=tk.LEFT, fill=tk. BOTH, expand=True)

        # ===== CONTENEDOR 2 COLUMNAS =====
        content = ttk.Frame(main)
        content.pack(fill=tk.BOTH, expand=True)

        # ===== COLUMNA IZQUIERDA:  Crear Subproducto =====
        left_panel = tk.LabelFrame(
            content,
            text="1️⃣ Crear Subproducto",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=10,
            pady=10,
            fg="#ffc107"
        )
        left_panel.pack(side=tk.LEFT, fill=tk. BOTH, expand=True, padx=(0, 10))

        # Nombre
        tk.Label(
            left_panel,
            text="Nombre del Subproducto:",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))

        self.sub_nombre_entry = tk.Entry(left_panel, font=("Segoe UI", 10), width=40)
        self.sub_nombre_entry.pack(fill=tk.X, pady=(0, 15))

        # Ingredientes
        tk.Label(
            left_panel,
            text="Ingredientes:",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(10, 5))

        # Frame agregar ingredientes
        ing_frame = ttk.Frame(left_panel)
        ing_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(ing_frame, text="Producto:  ").grid(row=0, column=0, sticky="w", padx=2)
        self.ing_producto_combo = ttk.Combobox(ing_frame, width=12, state="readonly")
        self.ing_producto_combo.grid(row=0, column=1, padx=2)

        ttk.Label(ing_frame, text="Cantidad: ").grid(row=0, column=2, sticky="w", padx=2)
        self.ing_cantidad_entry = tk.Entry(ing_frame, width=10, font=("Segoe UI", 9))
        self.ing_cantidad_entry.grid(row=0, column=3, padx=2)

        ttk.Label(ing_frame, text="Unidad: ").grid(row=0, column=4, sticky="w", padx=2)
        self.ing_unidad_combo = ttk.Combobox(
            ing_frame,
            values=["g", "kg", "ml", "L", "units"],
            state="readonly",
            width=10
        )
        self.ing_unidad_combo.grid(row=0, column=5, padx=2)

        add_btn = tk.Button(
            ing_frame,
            text="➕",
            command=self.add_ingredient,
            bg="#0078d4",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            relief=tk.FLAT
        )
        add_btn.grid(row=0, column=6, padx=5)

        # Tabla ingredientes
        cols = ("Producto", "Cantidad", "Unidad", "❌")
        self.ingredientes_tree = ttk.Treeview(left_panel, columns=cols, show="headings", height=6)
        self.ingredientes_tree.heading("Producto", text="Producto")
        self.ingredientes_tree.heading("Cantidad", text="Cantidad")
        self.ingredientes_tree. heading("Unidad", text="Unidad")
        self.ingredientes_tree.heading("❌", text="")

        self.ingredientes_tree. column("Producto", width=150)
        self.ingredientes_tree.column("Cantidad", width=80)
        self.ingredientes_tree.column("Unidad", width=70)
        self.ingredientes_tree.column("❌", width=30)

        self.ingredientes_tree.pack(fill=tk. BOTH, expand=True, pady=(0, 15))
        self.ingredientes_tree.bind("<Button-3>", self.on_ingrediente_right_click)

        # Botones
        btn_frame = tk. Frame(left_panel, bg="white")
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame,
            text="✅ Crear Subproducto",
            command=self.create_subproducto,
            bg="#198754",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8,
            relief=tk. FLAT
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🔄 Limpiar",
            command=self.clear_subproducto,
            bg="#6c757d",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        # ===== COLUMNA DERECHA =====
        right_panel = ttk.Frame(content)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # --- Subproductos (Superior) ---
        sub_card = tk.LabelFrame(
            right_panel,
            text="2️⃣ Subproductos",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=10,
            pady=10,
            fg="#0078d4"
        )
        sub_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        cols = ("Nombre", "Costo", "Acción")
        self.subproductos_tree = ttk. Treeview(sub_card, columns=cols, show="headings", height=5)
        self.subproductos_tree.heading("Nombre", text="📦 Nombre")
        self.subproductos_tree.heading("Costo", text="Costo Total")
        self.subproductos_tree.heading("Acción", text="")

        self.subproductos_tree.column("Nombre", width=200)
        self.subproductos_tree.column("Costo", width=100)
        self.subproductos_tree.column("Acción", width=50)

        self.subproductos_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.subproductos_tree.bind("<<TreeviewSelect>>", self. on_subproducto_select)
        self.subproductos_tree.bind("<Button-3>", self.on_subproducto_right_click)

        # Info subproducto
        info_frame = tk.Frame(sub_card, bg="white")
        info_frame.pack(fill=tk. X, pady=(5, 0))

        tk.Label(info_frame, text="Seleccionado:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        self.selected_sub_label = tk.Label(info_frame, text="(Ninguno)", font=("Segoe UI", 9), bg="white", fg="#0078d4")
        self.selected_sub_label.pack(anchor="w", padx=10)

        # Frame para producir subproductos
        produce_sub_frame = tk.Frame(sub_card, bg="white")
        produce_sub_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(produce_sub_frame, text="Cantidad a Producir:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        self.cantidad_producir_entry = tk.Entry(produce_sub_frame, font=("Segoe UI", 9), width=15)
        self.cantidad_producir_entry.insert(0, "1")
        self.cantidad_producir_entry.pack(anchor="w", padx=10, pady=(5, 10))

        tk.Button(
            sub_card,
            text="🚀 Producir Subproducto",
            command=self.produce_subproducto,
            bg="#d13438",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            relief=tk. FLAT
        ).pack(fill=tk.X)

        # --- Productos Finales (Inferior) ---
        prod_card = tk.LabelFrame(
            right_panel,
            text="3️⃣ Crear Productos Finales",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=10,
            pady=10,
            fg="#198754"
        )
        prod_card.pack(fill=tk.BOTH, expand=True)

        # Formulario para crear producto final
        form_frame = tk.Frame(prod_card, bg="white")
        form_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form_frame, text="Nombre del Producto:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w", pady=(0, 3))
        self.prod_nombre_entry = tk.Entry(form_frame, font=("Segoe UI", 9), width=40)
        self.prod_nombre_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form_frame, text="Subproducto Base:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w", pady=(0, 3))
        self.prod_subproducto_combo = ttk.Combobox(form_frame, state="readonly", width=40)
        self.prod_subproducto_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form_frame, text="Unidades Producidas:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w", pady=(0, 3))
        self.prod_unidades_entry = tk.Entry(form_frame, font=("Segoe UI", 9), width=15)
        self.prod_unidades_entry.insert(0, "1")
        self.prod_unidades_entry.pack(anchor="w", pady=(0, 10))

        tk.Button(
            form_frame,
            text="➕ Crear Producto Final",
            command=self.create_producto_final,
            bg="#198754",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8,
            relief=tk.FLAT
        ).pack(anchor="w")

        # Tabla de productos finales
        tk.Label(prod_card, text="Productos Creados:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w", pady=(15, 5))

        cols = ("Nombre", "Subproducto", "Unidades", "Costo Unit.", "Precio", "Margen", "")
        self.productos_tree = ttk.Treeview(prod_card, columns=cols, show="headings", height=4)
        self.productos_tree.heading("Nombre", text="📦 Nombre")
        self.productos_tree.heading("Subproducto", text="Subproducto")
        self.productos_tree.heading("Unidades", text="Unid.")
        self.productos_tree.heading("Costo Unit.", text="Costo Unit.")
        self.productos_tree.heading("Precio", text="Precio")
        self.productos_tree.heading("Margen", text="Margen %")
        self.productos_tree.heading("", text="")

        self.productos_tree.column("Nombre", width=100)
        self.productos_tree.column("Subproducto", width=90)
        self.productos_tree.column("Unidades", width=50)
        self.productos_tree.column("Costo Unit.", width=70)
        self.productos_tree.column("Precio", width=70)
        self.productos_tree.column("Margen", width=60)
        self.productos_tree.column("", width=30)

        self.productos_tree.pack(fill=tk. BOTH, expand=True)
        self.productos_tree. bind("<Button-3>", self.on_producto_right_click)

    # ===== MÉTODOS DE CARGA =====

    def load_ingredient_combo(self):
        """Cargar productos del inventario."""
        try:
            inventario = self.inv_backend. get_inventario_para_resumen()
            productos = [item['producto'] for item in inventario]
            self.ing_producto_combo['values'] = productos
        except Exception as e:
            self.logger.error(f"Error cargando ingredientes: {e}")

    def load_subproductos(self):
        """Cargar subproductos disponibles."""
        try:
            for item in self.subproductos_tree.get_children():
                self.subproductos_tree.delete(item)

            subproductos = self.backend.get_subproductos_disponibles()
            self.subproductos_map. clear()

            # También actualizar combo para productos finales
            sub_names = []

            for sub in subproductos:
                sub_id = sub. get('id')
                self.subproductos_map[sub_id] = sub
                nombre = sub.get('nombre', '')
                sub_names.append(nombre)

                self.subproductos_tree.insert(
                    "",
                    tk.END,
                    iid=str(sub_id),
                    values=(
                        nombre,
                        f"${sub.get('costo_total_subproducto', 0):.2f}",
                        "🗑️"
                    )
                )

            # Actualizar combo de subproductos para productos finales
            self.prod_subproducto_combo['values'] = sub_names

            self.logger.info(f"Cargados {len(subproductos)} subproductos")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar subproductos: {e}")
            self.logger.error(f"Error cargando subproductos: {e}")

    def load_productos_finales(self):
        """Cargar productos finales."""
        try:
            for item in self.productos_tree.get_children():
                self.productos_tree.delete(item)

            productos = self.backend.get_productos_finales_info()
            self.productos_finales_map. clear()

            for prod in productos:
                prod_id = prod.get('id')
                self.productos_finales_map[prod_id] = prod

                costo_unit = float(prod.get('costo_unitario', 0))
                precio = float(prod.get('precio_venta', 0) or 0)
                margen = float(prod.get('margen_ganancia', 0))
                unidades = int(prod.get('unidades_producidas', 1))

                self.productos_tree.insert(
                    "",
                    tk.END,
                    iid=str(prod_id),
                    values=(
                        prod. get('nombre', ''),
                        prod.get('subproducto_nombre', ''),
                        unidades,
                        f"${costo_unit:.4f}",
                        f"${precio:.2f}" if precio > 0 else "-",
                        f"{margen:.1f}%" if precio > 0 else "-",
                        "🗑️"
                    )
                )

            self.logger. info(f"Cargados {len(productos)} productos finales")

        except Exception as e: 
            messagebox.showerror("Error", f"No se pudieron cargar productos finales: {e}")
            self.logger. error(f"Error cargando productos finales: {e}")

    # ===== EVENTOS DE SELECCIÓN =====

    def on_subproducto_select(self, event):
        """Manejar selección de subproducto."""
        selection = self.subproductos_tree.selection()

        if selection:
            try:
                sub_id = int(selection[0])
                self.selected_subproducto_id = sub_id
                self. selected_subproducto_data = self.subproductos_map.get(sub_id)

                if self.selected_subproducto_data:
                    nombre = self.selected_subproducto_data. get('nombre')
                    costo = self.selected_subproducto_data.get('costo_total_subproducto', 0)
                    self. selected_sub_label.config(text=f"📦 {nombre} - ${costo:.2f}")
                    self.logger.info(f"Subproducto seleccionado:  {nombre}")

            except Exception as e:
                self.logger.error(f"Error seleccionando subproducto:  {e}")

    # ===== OPERACIONES INGREDIENTES =====

    def add_ingredient(self):
        """Agregar ingrediente a la tabla."""
        try:
            producto = self.ing_producto_combo.get()
            cantidad = self.ing_cantidad_entry.get().strip()
            unidad = self.ing_unidad_combo.get()

            if not all([producto, cantidad, unidad]):
                messagebox.showwarning("Aviso", "Completa todos los campos")
                return

            try: 
                float(cantidad)
            except ValueError:
                messagebox. showerror("Error", "La cantidad debe ser un número")
                return

            self.ingredientes_tree.insert("", tk.END, values=(producto, cantidad, unidad))
            self.ingredientes_list.append({
                'producto': producto,
                'cantidad': float(cantidad),
                'unidad': unidad
            })

            self.ing_producto_combo.set("")
            self.ing_cantidad_entry.delete(0, tk.END)
            self.ing_unidad_combo.set("")

        except Exception as e:
            messagebox.showerror("Error", f"Error:  {e}")

    def on_ingrediente_right_click(self, event):
        """Click derecho para eliminar ingrediente."""
        item = self.ingredientes_tree. identify('item', event.x, event. y)

        if not item:
            return

        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(
            label="❌ Eliminar",
            command=lambda: self.remove_ingrediente(item),
            foreground="red"
        )

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def remove_ingrediente(self, item_id):
        """Eliminar ingrediente."""
        try:
            values = self.ingredientes_tree. item(item_id, 'values')
            self.ingredientes_tree.delete(item_id)

            self.ingredientes_list = [
                ing for ing in self.ingredientes_list
                if ing['producto'] != values[0]
            ]

        except Exception as e:
            self.logger.error(f"Error eliminando ingrediente: {e}")

    # ===== OPERACIONES SUBPRODUCTOS =====

    def create_subproducto(self):
        """Crear nuevo subproducto."""
        try:
            nombre = self.sub_nombre_entry.get().strip()

            if not nombre or not self.ingredientes_list:
                messagebox.showwarning("Aviso", "Ingresa nombre y al menos un ingrediente")
                return

            costo = self.backend.crear_subproducto(nombre, self.ingredientes_list)

            messagebox.showinfo(
                "✅ Éxito",
                f"Subproducto '{nombre}' creado\nCosto Total: ${costo:.2f}"
            )

            self.clear_subproducto()
            self.load_subproductos()

        except Exception as e:
            messagebox.showerror("Error", f"Error:  {e}")
            self.logger.error(f"Error creando subproducto: {e}")

    def produce_subproducto(self):
        """Producir subproducto (consumir ingredientes)."""
        if not self.selected_subproducto_id:
            messagebox.showwarning("Aviso", "Selecciona un subproducto")
            return

        try: 
            cantidad_str = self.cantidad_producir_entry.get().strip()
            try:
                cantidad = int(float(cantidad_str))
                if cantidad <= 0:
                    messagebox.showwarning("Aviso", "La cantidad debe ser mayor a 0")
                    return
            except ValueError:
                messagebox.showerror("Error", "Ingresa una cantidad válida")
                return

            # Llamar al backend para producir
            sub_data = self.backend.producir_subproducto(
                self.selected_subproducto_id,
                cantidad
            )

            messagebox.showinfo(
                "✅ Éxito",
                f"Subproducto '{sub_data['nombre']}' producido x{cantidad}\n"
                f"Ingredientes consumidos del inventario"
            )

            self.cantidad_producir_entry.delete(0, tk.END)
            self.cantidad_producir_entry.insert(0, "1")
            self.load_subproductos()

        except Exception as e:
            messagebox.showerror("Error", f"Error:  {e}")
            self.logger.error(f"Error produciendo:  {e}")

    def on_subproducto_right_click(self, event):
        """Click derecho en subproducto."""
        item = self.subproductos_tree.identify('item', event.x, event. y)

        if not item: 
            return

        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(
            label="❌ Eliminar",
            command=lambda: self.delete_subproducto(int(item)),
            foreground="red"
        )

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def delete_subproducto(self, sub_id):
        """Eliminar subproducto."""
        if not messagebox.askyesno("Confirmar", "¿Eliminar este subproducto?"):
            return

        try:
            self.backend.eliminar_subproducto(sub_id)
            self.load_subproductos()
            self.load_productos_finales()
            messagebox.showinfo("✅ Éxito", "Subproducto eliminado")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    # ===== OPERACIONES PRODUCTOS FINALES =====

    def create_producto_final(self):
        """Crear nuevo producto final con cálculo automático de costo por unidad."""
        try:
            nombre = self.prod_nombre_entry.get().strip()
            subproducto_nombre = self.prod_subproducto_combo. get()
            unidades_str = self.prod_unidades_entry.get().strip()

            if not nombre or not subproducto_nombre or not unidades_str:
                messagebox.showwarning("Aviso", "Completa todos los campos")
                return

            try:
                unidades = int(float(unidades_str))
                if unidades <= 0:
                    messagebox.showwarning("Aviso", "Las unidades deben ser mayor a 0")
                    return
            except ValueError:
                messagebox.showerror("Error", "Las unidades deben ser un número")
                return

            # Obtener ID del subproducto seleccionado
            subproducto_id = None
            for sub_id, sub_data in self.subproductos_map.items():
                if sub_data. get('nombre') == subproducto_nombre:
                    subproducto_id = sub_id
                    break

            if not subproducto_id: 
                messagebox.showerror("Error", "Subproducto no encontrado")
                return

            # Crear producto final
            self.backend.crear_producto_final(nombre, subproducto_id, unidades, 0)

            costo_total = float(self.subproductos_map[subproducto_id].get('costo_total_subproducto', 0))
            costo_unitario = costo_total / unidades

            messagebox.showinfo(
                "✅ Éxito",
                f"Producto final '{nombre}' creado\n"
                f"Subproducto: {subproducto_nombre}\n"
                f"Unidades Producidas: {unidades}\n"
                f"Costo Unitario: ${costo_unitario:.4f}"
            )

            # Limpiar formulario
            self.prod_nombre_entry.delete(0, tk.END)
            self.prod_subproducto_combo.set("")
            self.prod_unidades_entry.delete(0, tk.END)
            self.prod_unidades_entry.insert(0, "1")

            self.load_productos_finales()

        except Exception as e:
            messagebox. showerror("Error", f"Error: {e}")
            self.logger.error(f"Error creando producto final: {e}")

    def on_producto_right_click(self, event):
        """Click derecho en producto final."""
        item = self.productos_tree.identify('item', event.x, event.y)

        if not item:
            return

        context_menu = tk. Menu(self, tearoff=0)
        context_menu.add_command(
            label="❌ Eliminar",
            command=lambda: self.delete_producto(int(item)),
            foreground="red"
        )

        try:
            context_menu. tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def delete_producto(self, prod_id):
        """Eliminar producto final."""
        if not messagebox.askyesno("Confirmar", "¿Eliminar este producto? "):
            return

        try: 
            self.backend.eliminar_producto_final(prod_id)
            self.load_productos_finales()
            messagebox.showinfo("✅ Éxito", "Producto eliminado")
        except Exception as e:
            messagebox.showerror("Error", f"Error:  {e}")

    # ===== LIMPIAR =====

    def clear_subproducto(self):
        """Limpiar formulario."""
        self.sub_nombre_entry.delete(0, tk. END)
        for item in self.ingredientes_tree.get_children():
            self.ingredientes_tree.delete(item)
        self.ingredientes_list. clear()
        self.ing_producto_combo.set("")
        self.ing_cantidad_entry.delete(0, tk.END)
        self.ing_unidad_combo.set("")