from Core.database import get_connection, insert_compra, get_compras
from Core.logger import setup_logger
from Core.inventario_backend import InventarioBackend

class ComprasBackend:
    def __init__(self):
        self.db = get_connection()
        self.logger = setup_logger()
        self.inventory_maneger = InventarioBackend()
        self.logger.info("ComprasBackend initialized")

    def save_purchase(self, tipo, nombre, proveedor, cantidad=None, unidad=None, precio_compra=None, cantidad_paq=None, precio_paq=None, peso_paq=None, unidad_peso=None):
        self.logger.info(f"Attempting to save {tipo} purchase: {nombre}")
        if not nombre or not proveedor:
            self.logger.warning("Save purchase failed: missing product name or supplier")
            raise ValueError("Nombre del producto y proveedor son obligatorios")
        try:
            if tipo == "granel":
                cantidad = float(cantidad)
                precio_compra = float(precio_compra)
                precio_total = precio_compra * cantidad
                if not unidad:
                    raise ValueError("Unidad es obligatoria")
                insert_compra(nombre, str(cantidad), unidad, precio_compra, precio_total, proveedor, "granel")
                self.inventory_maneger.actualizar_stock_desde_compra(nombre, cantidad, unidad, precio_total)
                self.logger.info(f"Saved granel purchase: {nombre}, {cantidad} {unidad}, ${precio_total}")
            elif tipo == "paquetes":
                cantidad_paq = int(cantidad_paq)
                precio_paq = float(precio_paq)
                peso_paq = float(peso_paq)
                if not unidad_peso:
                    raise ValueError("Unidad de peso es obligatoria")
                cantidad_total_peso = cantidad_paq * peso_paq
                precio_total = cantidad_paq * precio_paq
                cantidad_str = f"{cantidad_paq} x {peso_paq} {unidad_peso}"
                insert_compra(nombre, cantidad_total_peso, unidad_peso, precio_paq, precio_total, proveedor, "paquetes")
                self.inventory_maneger.actualizar_stock_desde_compra(nombre, cantidad_total_peso, unidad_peso, precio_total)
                self.logger.info(f"Saved paquetes purchase: {nombre}, {cantidad_paq} paquetes, ${precio_paq} each")
            else:
                raise ValueError("Tipo de compra inválido")
        except ValueError as e:
            self.logger.error(f"Save purchase failed due to invalid input: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Save purchase failed: {e}")
            raise

    def get_purchase_history(self):
        self.logger.info("Retrieving purchase history")
        return get_compras()



        