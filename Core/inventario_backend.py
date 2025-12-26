# Codigo 1 backend de la ui (refactorizado)

from Core.database import get_connection
from Core.logger import setup_logger
from Core.units import convert_to_base, convert_from_base, CONVERSIONS

class InventarioBackend:
    def __init__(self):
        self.database = get_connection()
        self.logger = setup_logger()
        self.logger.info("InventarioBackend initialized")

    def _get_unidad_base(self, unidad):
        """Determina la unidad base a partir de una unidad dada."""
        unidad = unidad.lower()
        for category, units in CONVERSIONS.items():
            if unidad in units:
                if category == 'weight': return 'g'
                if category == 'volume': return 'ml'
                if category == 'count': return 'unit'
        return None

    def actualizar_stock_desde_compra(self, producto, cantidad, unidad, precio_total):
        """Añade stock al inventario y recalcula el costo promedio."""
        conn = get_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                unidad_base = self._get_unidad_base(unidad)
                if not unidad_base:
                    raise ValueError(f"Unidad '{unidad}' no reconocida.")

                cantidad_base, _ = convert_to_base(float(cantidad), unidad)
                if not cantidad_base:
                    raise ValueError("No se pudo convertir la cantidad a la unidad base.")

                # Verificar si el producto ya existe
                cursor.execute("SELECT cantidad_stock, costo_promedio_ponderado FROM inventario WHERE producto = %s", (producto,))
                result = cursor.fetchone()

                if result:
                    # Producto existe: actualizar stock y costo promedio
                    stock_actual, costo_actual = float(result['cantidad_stock']), float(result['costo_promedio_ponderado'])
                    nuevo_stock = stock_actual + cantidad_base
                    # Fórmula del costo promedio ponderado
                    nuevo_costo_promedio = ((stock_actual * costo_actual) + precio_total) / nuevo_stock
                    cursor.execute(
                        "UPDATE inventario SET cantidad_stock = %s, costo_promedio_ponderado = %s WHERE producto = %s",
                        (nuevo_stock, nuevo_costo_promedio, producto)
                    )
                    self.logger.info(f"Updated stock for {producto}: +{cantidad_base} {unidad_base}, new total: {nuevo_stock}")
                else:
                    # Producto no existe: insertar nuevo
                    costo_unitario_base = precio_total / cantidad_base
                    cursor.execute(
                        "INSERT INTO inventario (producto, cantidad_stock, unidad_base, costo_promedio_ponderado) VALUES (%s, %s, %s, %s)",
                        (producto, cantidad_base, unidad_base, costo_unitario_base)
                    )
                    self.logger.info(f"Inserted new product in inventory: {producto}")

            conn.commit()
        except Exception as e:
            self.logger.error(f"Error updating stock from purchase: {e}")
            conn.rollback()
        finally:
            conn.close()

    def consumir_stock(self, producto, cantidad_a_consumir, unidad_consumo):
        """Reduce el stock de un producto. Lanza un error si no hay suficiente."""
        conn = get_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                # Obtener stock actual
                cursor.execute("SELECT cantidad_stock, unidad_base FROM inventario WHERE producto = %s", (producto,))
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"El producto '{producto}' no existe en el inventario.")

                stock_actual_base, unidad_base_db = float(result['cantidad_stock']), result['unidad_base']

                # Convertir la cantidad a consumir a la unidad base de la DB
                cantidad_base_a_consumir, _ = convert_to_base(float(cantidad_a_consumir), unidad_consumo)
                if not cantidad_base_a_consumir:
                    raise ValueError(f"No se pudo convertir la cantidad de consumo '{cantidad_a_consumir} {unidad_consumo}'")

                if stock_actual_base < cantidad_base_a_consumir:
                    raise ValueError(f"Stock insuficiente para '{producto}'. Disponible: {stock_actual_base:.2f} {unidad_base_db}, Requerido: {cantidad_base_a_consumir:.2f} {unidad_base_db}")

                # Actualizar stock
                nuevo_stock = stock_actual_base - cantidad_base_a_consumir
                cursor.execute("UPDATE inventario SET cantidad_stock = %s WHERE producto = %s", (nuevo_stock, producto))
            conn.commit()
        except Exception as e:
            self.logger.error(f"Error consumiendo stock: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    # Core/inventario_backend.py (continuation)

    def get_inventario_para_resumen(self):
        """
        Fetches all items from the inventory table, ready for display.
        """
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                # We only care about items we actually have in stock
                cursor.execute("SELECT producto, cantidad_stock, unidad_base, costo_promedio_ponderado FROM inventario WHERE cantidad_stock > 0")
                results = cursor.fetchall()
                
                # Here's where we implement the dynamic unit display logic
                processed_results = []
                for item in results:
                    producto = item['producto']
                    cantidad_base = float(item['cantidad_stock']) # e.g., 800.0
                    unidad_base = item['unidad_base']      # e.g., 'g'
                    costo_por_base = float(item['costo_promedio_ponderado']) # e.g., 0.175

                    # --- Dynamic Unit Conversion Logic ---
                    display_cantidad = cantidad_base
                    display_unidad = unidad_base

                    if unidad_base == 'g':
                        if cantidad_base >= 1000:
                            display_cantidad = cantidad_base / 1000
                            display_unidad = 'kg'
                    elif unidad_base == 'ml':
                        if cantidad_base >= 1000:
                            display_cantidad = cantidad_base / 1000
                            display_unidad = 'l'
                    # You can add more rules here for other units if needed

                    # --- Calculate Display Values ---
                    # The total value of the stock for this item
                    total_valor = cantidad_base * costo_por_base

                    # The cost per base unit (e.g., cost per g)
                    costo_por_display_unidad = costo_por_base

                    processed_results.append({
                        "producto": producto,
                        "cantidad_display": f"{display_cantidad:.2f}",
                        "unidad_display": display_unidad,
                        "costo_promedio_display": f"${costo_por_display_unidad:.4f}", # e.g., $/kg
                        "total_valor": total_valor
                    })
                    
                return processed_results
        except Exception as e:
            self.logger.error(f"Error retrieving summary inventory: {e}")
            return []
        finally:
            conn.close()


    # def get_inventario(self):
    #     self.logger.info("Retrieving inventory data")
    #     conn = get_connection()
    #     if conn:
    #         try:
    #             with conn.cursor() as cursor:
    #                 cursor.execute("""
    #                     SELECT producto,
    #                            SUM(CASE WHEN tipo = 'granel' THEN CAST(cantidad AS DECIMAL(10,2)) ELSE 0 END) as cantidad_granel,
    #                            SUM(CASE WHEN tipo = 'paquetes' THEN CAST(SUBSTRING_INDEX(cantidad, ' x ', 1) AS DECIMAL(10,2)) * CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cantidad, ' x ', -1), ' ', 1) AS DECIMAL(10,2)) ELSE 0 END) as cantidad_paquetes,
    #                            unidad,
    #                            AVG(precio_compra) as costo_promedio,
    #                            SUM(precio_total) as total_precio
    #                     FROM compras
    #                     GROUP BY producto, unidad
    #                     ORDER BY producto
    #                 """)
    #                 results = cursor.fetchall()

    #                 # --- ESTA PARTE SE MANTIENE IGUAL ---
    #                 # Itera sobre los resultados y aplica la función de cálculo a cada uno
    #                 processed_results = []
    #                 for item in results:
    #                     calculated_item = calculate_cost_per_base_unit(item)
    #                     processed_results.append(calculated_item)

    #                 return processed_results

    #         except Exception as e:
    #             self.logger.error(f"Error retrieving inventory: {e}")
    #             return []
    #         finally:
    #             conn.close()
    #     return []