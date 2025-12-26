import tkinter as tk
from tkinter import ttk, messagebox
from Gui.Pages.Styles.compras_styles import CompraStyles
from Core.compras_backend import ComprasBackend
from Core.logger import setup_logger

class ComprasFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.backend = ComprasBackend()
        self.styles = CompraStyles()
        self.logger = setup_logger()
        self.setup_ui()

    def setup_ui(self):
        # Main container with modern card design
        main_card = tk.Frame(self, bg="#ffffff", relief="flat", bd=1)
        main_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_card, text="Compras de Productos", font=("Segoe UI", 20, "bold"), foreground="#323130")
        title_label.pack(pady=(25, 15))

        type_frame = ttk.Frame(main_card)
        type_frame.pack(pady=5, padx=25)
        ttk.Label(type_frame, text="Tipo de compras:").pack(side=tk.LEFT)
        self.tipo_var = tk.StringVar(value="granel")
        ttk.Radiobutton(type_frame, text="A Granel", variable=self.tipo_var, value="granel", command=self.update_fields).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(type_frame, text="Paquetes", variable=self.tipo_var, value="paquetes", command=self.update_fields).pack(side=tk.LEFT)

        # Form container with modern card
        form_card = tk.Frame(main_card, bg="#f8f8f8", relief="flat", bd=1)
        form_card.pack(fill=tk.X, padx=25, pady=(0, 20))
        self.form_frame = ttk.Frame(form_card)
        self.form_frame.pack(pady=15, padx=15, fill=tk.X)

        ttk.Label(self.form_frame, text="Nombre del Producto:" ).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.nombre_entry = ttk.Entry(self.form_frame)
        self.nombre_entry.grid(row=0, column=1, sticky=tk.EW)

        ttk.Label(self.form_frame, text="Proveedor:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.proveedor_entry = ttk.Entry(self.form_frame)
        self.proveedor_entry.grid(row=1, column=1, pady=2, sticky=tk.EW)

        # Granel fields
        self.granel_frame = ttk.Frame(self.form_frame)
        ttk.Label(self.granel_frame, text="Cantidad:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cantidad_entry = ttk.Entry(self.granel_frame)
        self.cantidad_entry.grid(row=0, column=1, pady=2)
        ttk.Label(self.granel_frame, text="Unidad:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.unidad_combo = ttk.Combobox(self.granel_frame, values=["g", "kg", "lb", "oz", "ml", "liters", "units"])
        self.unidad_combo.grid(row=0, column=3, pady=2)
        ttk.Label(self.granel_frame, text="Precio Compra:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.precio_entry = ttk.Entry(self.granel_frame)
        self.precio_entry.grid(row=1, column=1, pady=2)

        # Paquetes fields
        self.paquetes_frame = ttk.Frame(self.form_frame)
        ttk.Label(self.paquetes_frame, text="Cantidad de Paquetes:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cantidad_paq_entry = ttk.Entry(self.paquetes_frame)
        self.cantidad_paq_entry.grid(row=0, column=1, pady=2)
        ttk.Label(self.paquetes_frame, text="Precio por Paquete:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.precio_paq_entry = ttk.Entry(self.paquetes_frame)
        self.precio_paq_entry.grid(row=1, column=1, pady=2)
        ttk.Label(self.paquetes_frame, text="Peso por Paquete:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.peso_paq_entry = ttk.Entry(self.paquetes_frame)
        self.peso_paq_entry.grid(row=2, column=1, pady=2)
        ttk.Label(self.paquetes_frame, text="Unidad de Peso:").grid(row=2, column=2, sticky=tk.W, pady=2)
        self.unidad_peso_combo = ttk.Combobox(self.paquetes_frame, values=["g", "kg", "lb", "oz", "ml", "units"])
        self.unidad_peso_combo.grid(row=2, column=3, pady=2)

        # History treeview
        history_frame = ttk.Frame(main_card)
        history_frame.pack(pady=10, padx=25, fill=tk.BOTH, expand=True)
        ttk.Label(history_frame, text="Historial de Compras", font=("Segoe UI", 14, "bold")).pack(pady=5)
        columns = ("Producto", "Cantidad", "Unidad", "Precio Compra", "Precio Total", "Proveedor", "Tipo", "Fecha")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10, style="Modern.Treeview")
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        self.history_tree.pack(fill=tk.BOTH, expand=True)

        # Buttons with modern styling
        button_frame = ttk.Frame(form_card)
        button_frame.pack(pady=(10, 15))
        ttk.Button(button_frame, text="Guardar Compra", command=self.save_purchase, style="Primary.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cargar Historial", command=self.load_history, style="Secondary.TButton").pack(side=tk.LEFT)

        # Initialize form fields visibility
        self.update_fields()
        self.load_history()

        self.update_fields()
        self.load_history()

    def update_fields(self):
        tipo = self.tipo_var.get()
        if tipo == "granel":
            self.granel_frame.grid(row=2, column=0, columnspan=2, pady=5)
            self.paquetes_frame.grid_forget()
        else:
            self.paquetes_frame.grid(row=2, column=0, columnspan=2, pady=5)
            self.granel_frame.grid_forget()

    def save_purchase(self):
        nombre = self.nombre_entry.get()
        proveedor = self.proveedor_entry.get()
        tipo = self.tipo_var.get()
        try:
            if tipo == "granel":
                cantidad = self.cantidad_entry.get()
                unidad = self.unidad_combo.get()
                precio_compra = self.precio_entry.get()
                self.backend.save_purchase(tipo, nombre, proveedor, cantidad=cantidad, unidad=unidad, precio_compra=precio_compra)
            else:
                cantidad_paq = self.cantidad_paq_entry.get()
                precio_paq = self.precio_paq_entry.get()
                peso_paq = self.peso_paq_entry.get()
                unidad_peso = self.unidad_peso_combo.get()
                self.backend.save_purchase(tipo, nombre, proveedor, cantidad_paq=cantidad_paq, precio_paq=precio_paq, peso_paq=peso_paq, unidad_peso=unidad_peso)
            messagebox.showinfo("Éxito", "Compra guardada exitosamente")
            self.clear_form()
            self.load_history()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la compra: {e}")

    def load_history(self):
        try:
            history = self.backend.get_purchase_history()
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            for purchase in history:
                self.history_tree.insert("", tk.END, values=(
                    purchase['producto'], purchase['cantidad'], purchase['unidad'],
                    purchase['precio_compra'], purchase['precio_total'], purchase['proveedor'], purchase['tipo'], purchase['fecha']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el historial: {e}")

    def clear_form(self):
        self.nombre_entry.delete(0, tk.END)
        self.proveedor_entry.delete(0, tk.END)
        self.cantidad_entry.delete(0, tk.END)
        self.precio_entry.delete(0, tk.END)
        self.cantidad_paq_entry.delete(0, tk.END)
        self.precio_paq_entry.delete(0, tk.END)
        self.peso_paq_entry.delete(0, tk.END)
