"""
Tab de Contabilidad - Gestión de ingresos, gastos, inversiones y fondos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from Core.inventario_backend import InventarioBackend
from Core.logger import setup_logger
from decimal import Decimal


class ContabilidadTab(ttk.Frame):
    """Tab para gestionar contabilidad del negocio."""
    
    tab_name = "Contabilidad"
    
    def __init__(self, parent, backend:  InventarioBackend):
        super().__init__(parent)
        self.backend = backend
        self.logger = setup_logger()
        
        # Variables de contabilidad
        self.total_inversiones = Decimal(0)
        self.total_ganancias = Decimal(0)
        self.total_gastos = Decimal(0)
        self.fondo_negocio = Decimal(0)
        self.capital_disponible = Decimal(0)
        
        self.setup_ui()
        self.load_contabilidad()
        self.logger.info("ContabilidadTab initialized")
    
    def setup_ui(self):
        """Configurar la interfaz."""
        
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ===== SECCIÓN 1: Resumen Ejecutivo =====
        resumen_card = tk.LabelFrame(
            main,
            text="📈 Resumen Ejecutivo",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=15,
            pady=15,
            fg="#0078d4"
        )
        resumen_card. pack(fill=tk.X, pady=(0, 15))
        
        # Crear grid para los indicadores
        indicators_frame = ttk.Frame(resumen_card)
        indicators_frame.pack(fill=tk.X)
        
        # Indicador 1: Total de Inversiones
        self._create_indicator(
            indicators_frame, 0, 0,
            "💵 Total Inversiones",
            "$0.00",
            "inversiones_label"
        )
        
        # Indicador 2: Total de Ganancias
        self._create_indicator(
            indicators_frame, 0, 1,
            "💰 Ganancias Reales",
            "$0.00",
            "ganancias_label"
        )
        
        # Indicador 3: Total de Gastos
        self._create_indicator(
            indicators_frame, 0, 2,
            "💸 Total Gastos",
            "$0.00",
            "gastos_label"
        )
        
        # Indicador 4: Fondo del Negocio
        self._create_indicator(
            indicators_frame, 1, 0,
            "🏦 Fondo de Negocio (20%)",
            "$0.00",
            "fondo_label"
        )
        
        # Indicador 5: Capital Disponible
        self._create_indicator(
            indicators_frame, 1, 1,
            "💎 Capital Disponible",
            "$0.00",
            "capital_label"
        )
        
        # Indicador 6: Estado del Negocio
        self._create_indicator(
            indicators_frame, 1, 2,
            "📊 Margen Neto",
            "0.00%",
            "margen_label"
        )
        
        # ===== SECCIÓN 2: Detalles de Inventario e Inversión =====
        detalles_card = tk.LabelFrame(
            main,
            text="📦 Detalles de Inversiones en Inventario",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=10,
            pady=10,
            fg="#198754"
        )
        detalles_card.pack(fill=tk. BOTH, expand=True, pady=(0, 15))
        
        # Tabla de inventario con costos
        cols = ("Producto", "Cantidad", "Unidad", "Costo Unit.", "Inversión Total")
        self.inventario_tree = ttk.Treeview(
            detalles_card,
            columns=cols,
            show="headings",
            height=10
        )
        
        self.inventario_tree. heading("Producto", text="📦 Producto")
        self.inventario_tree.heading("Cantidad", text="Cantidad")
        self.inventario_tree.heading("Unidad", text="Unidad")
        self.inventario_tree.heading("Costo Unit.", text="Costo Unit.")
        self.inventario_tree.heading("Inversión Total", text="Inversión Total")
        
        self.inventario_tree.column("Producto", width=200)
        self.inventario_tree.column("Cantidad", width=100, anchor=tk.CENTER)
        self.inventario_tree.column("Unidad", width=80, anchor=tk.CENTER)
        self.inventario_tree. column("Costo Unit.", width=100, anchor=tk.E)
        self.inventario_tree.column("Inversión Total", width=150, anchor=tk.E)
        
        self.inventario_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk. Scrollbar(
            detalles_card,
            orient=tk.VERTICAL,
            command=self.inventario_tree.yview
        )
        self.inventario_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ===== SECCIÓN 3: Historial de Movimientos =====
        movimientos_card = tk.LabelFrame(
            main,
            text="📜 Historial de Movimientos",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=10,
            pady=10,
            fg="#0dcaf0"
        )
        movimientos_card.pack(fill=tk.BOTH, expand=True)
        
        # Tabla de movimientos
        mov_cols = ("Fecha", "Tipo", "Descripción", "Monto")
        self.movimientos_tree = ttk.Treeview(
            movimientos_card,
            columns=mov_cols,
            show="headings",
            height=8
        )
        
        self.movimientos_tree.heading("Fecha", text="📅 Fecha")
        self.movimientos_tree.heading("Tipo", text="Tipo")
        self.movimientos_tree.heading("Descripción", text="Descripción")
        self.movimientos_tree.heading("Monto", text="Monto")
        
        self.movimientos_tree.column("Fecha", width=120, anchor=tk.CENTER)
        self.movimientos_tree.column("Tipo", width=80, anchor=tk.CENTER)
        self.movimientos_tree.column("Descripción", width=300)
        self.movimientos_tree.column("Monto", width=100, anchor=tk.E)
        
        self.movimientos_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar
        mov_scrollbar = ttk. Scrollbar(
            movimientos_card,
            orient=tk. VERTICAL,
            command=self.movimientos_tree.yview
        )
        self.movimientos_tree.configure(yscroll=mov_scrollbar.set)
        mov_scrollbar. pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón de actualizar
        refresh_btn = tk.Button(
            movimientos_card,
            text="🔄 Actualizar",
            command=self.load_contabilidad,
            bg="#0078d4",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.RIGHT, pady=(10, 0))
    
    def _create_indicator(self, parent, row, col, label, value, attr_name):
        """Crear un indicador de estado."""
        frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10, ipadx=10, ipady=10)
        
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        tk.Label(
            frame,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#323130"
        ).pack(anchor="w")
        
        value_label = tk.Label(
            frame,
            text=value,
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#0078d4"
        )
        value_label.pack(anchor="w", pady=(5, 0))
        
        # Guardar referencia al label para actualizarlo después
        setattr(self, attr_name, value_label)
    
    def load_contabilidad(self):
        """Cargar datos de contabilidad."""
        try:
            # Limpiar tablas
            for item in self.inventario_tree. get_children():
                self. inventario_tree.delete(item)
            for item in self. movimientos_tree.get_children():
                self.movimientos_tree.delete(item)
            
            # Obtener datos del inventario
            inventario = self.backend.get_inventario_para_resumen()
            
            total_inversiones = Decimal(0)
            
            for item in inventario: 
                total_inversiones += Decimal(str(item['total_valor']))
                
                self.inventario_tree.insert(
                    "",
                    tk.END,
                    values=(
                        item['producto'],
                        item['cantidad_display'],
                        item['unidad_display'],
                        item['costo_promedio_display'],
                        f"${item['total_valor']:.2f}"
                    )
                )
            
            self.total_inversiones = total_inversiones
            
            # Actualizar indicadores (valores de ejemplo, se pueden conectar a BD)
            self._update_indicators()
            
            # Agregar movimientos de ejemplo
            self._load_sample_movements()
            
            self.logger.info("Contabilidad cargada")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando contabilidad: {e}")
            self.logger.error(f"Error en load_contabilidad: {e}")
    
    def _update_indicators(self):
        """Actualizar indicadores de estado."""
        # Estos valores deberían venir de la base de datos
        # Por ahora usamos valores de ejemplo
        
        self.inversiones_label.config(text=f"${float(self.total_inversiones):.2f}")
        
        # Calcular margen neto (ganancias - gastos - inversiones)
        margen = self.total_ganancias - self.total_gastos
        margen_pct = (float(margen) / float(self.total_inversiones) * 100) if self.total_inversiones > 0 else 0
        
        self. ganancias_label.config(text=f"${float(self.total_ganancias):.2f}")
        self.gastos_label.config(text=f"${float(self.total_gastos):.2f}")
        self.fondo_label.config(text=f"${float(self.fondo_negocio):.2f}")
        self.capital_label.config(text=f"${float(self.capital_disponible):.2f}")
        self.margen_label.config(text=f"{margen_pct:.2f}%")
    
    def _load_sample_movements(self):
        """Cargar movimientos de ejemplo."""
        movements = [
            {
                'fecha': datetime.now().strftime("%Y-%m-%d"),
                'tipo': "Inversión",
                'descripcion':  "Compra de inventario inicial",
                'monto': float(self.total_inversiones)
            },
            {
                'fecha': datetime.now().strftime("%Y-%m-%d"),
                'tipo': "Venta",
                'descripcion':  "Venta de productos",
                'monto': 150.00
            },
            {
                'fecha': datetime.now().strftime("%Y-%m-%d"),
                'tipo': "Fondo",
                'descripcion':  "Transferencia a fondo del negocio (20%)",
                'monto': 30.00
            }
        ]
        
        for mov in movements:
            self. movimientos_tree.insert(
                "",
                tk.END,
                values=(
                    mov['fecha'],
                    mov['tipo'],
                    mov['descripcion'],
                    f"${mov['monto']:.2f}"
                )
            )