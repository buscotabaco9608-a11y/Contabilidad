"""
Backend para la gestión de producción. 
Maneja subproductos, productos finales e ingredientes.
"""

import pymysql
from decimal import Decimal
from Core.database import get_connection
from Core.logger import setup_logger
from Core.inventario_backend import InventarioBackend
from Core.units import convert_to_base

logger = setup_logger()


class ProduccionBackend: 
    def __init__(self):
        self.db = get_connection()
        self.inventory_manager = InventarioBackend()
        logger.info("ProduccionBackend initialized")

    # ===== SUBPRODUCTOS =====

    def crear_subproducto(self, nombre_subproducto, ingredientes):
        """
        Crear un subproducto y consumir ingredientes del inventario. 

        Args:
            nombre_subproducto:  Nombre del subproducto
            ingredientes: Lista de dicts con 'producto', 'cantidad', 'unidad'

        Returns: 
            El costo total del subproducto
        """
        conn = get_connection()
        if not conn:
            raise Exception("No database connection")

        total_costo = Decimal(0)
        try:
            # Fase 1: Calcular costo y validar stock
            with conn.cursor() as cursor:
                for ing in ingredientes:
                    producto = ing['producto']
                    cantidad = ing['cantidad']
                    unidad = ing['unidad']

                    cursor.execute(
                        "SELECT costo_promedio_ponderado FROM inventario WHERE producto = %s",
                        (producto,)
                    )
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError(f"El ingrediente '{producto}' no está en el inventario")

                    costo_por_base = result['costo_promedio_ponderado']
                    cantidad_base, _ = convert_to_base(cantidad, unidad)
                    if not cantidad_base:
                        raise ValueError(f"No se pudo convertir cantidad para '{producto}'")

                    total_costo += Decimal(cantidad_base) * Decimal(costo_por_base)

            # Fase 2: Consumir stock
            for ing in ingredientes: 
                self.inventory_manager.consumir_stock(
                    ing['producto'],
                    ing['cantidad'],
                    ing['unidad']
                )

            # Fase 3: Guardar en BD
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO subproductos (nombre, costo_total_subproducto) VALUES (%s, %s)",
                    (nombre_subproducto, total_costo)
                )
                subproducto_id = cursor. lastrowid

                for ing in ingredientes:
                    cursor. execute(
                        "INSERT INTO subproducto_ingredientes "
                        "(subproducto_id, producto_ingrediente, cantidad_usada, unidad_usada) "
                        "VALUES (%s, %s, %s, %s)",
                        (subproducto_id, ing['producto'], ing['cantidad'], ing['unidad'])
                    )

            conn.commit()
            logger.info(f"Subproducto '{nombre_subproducto}' creado.  Costo: ${total_costo:.2f}")
            return total_costo

        except Exception as e:
            logger.error(f"Error al crear subproducto: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_subproductos_disponibles(self):
        """Obtener todos los subproductos disponibles."""
        conn = get_connection()
        if not conn: 
            return []

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, costo_total_subproducto FROM subproductos ORDER BY nombre"
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo subproductos: {e}")
            return []
        finally:
            conn.close()

    def get_subproducto_ingredientes(self, subproducto_id):
        """Obtener ingredientes de un subproducto específico."""
        conn = get_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT producto_ingrediente, cantidad_usada, unidad_usada "
                    "FROM subproducto_ingredientes WHERE subproducto_id = %s",
                    (subproducto_id,)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo ingredientes:  {e}")
            return []
        finally:
            conn.close()

    def producir_subproducto(self, subproducto_id, cantidad_producida):
        """
        Producir un subproducto (consume ingredientes).

        Args:
            subproducto_id: ID del subproducto
            cantidad_producida: Cantidad a producir

        Returns:
            Información del subproducto producido
        """
        conn = get_connection()
        if not conn:
            raise Exception("No database connection")

        try:
            with conn.cursor() as cursor:
                # Obtener datos del subproducto
                cursor.execute(
                    "SELECT id, nombre, costo_total_subproducto FROM subproductos WHERE id = %s",
                    (subproducto_id,)
                )
                subproducto = cursor.fetchone()
                if not subproducto:
                    raise ValueError("Subproducto no encontrado")

                # Obtener ingredientes
                ingredientes = self.get_subproducto_ingredientes(subproducto_id)
                if not ingredientes:
                    raise ValueError("El subproducto no tiene ingredientes")

                # Consumir ingredientes
                for ing in ingredientes:
                    # Multiplicar cantidad por la cantidad a producir
                    cantidad_a_consumir = ing['cantidad_usada'] * cantidad_producida
                    self.inventory_manager.consumir_stock(
                        ing['producto_ingrediente'],
                        cantidad_a_consumir,
                        ing['unidad_usada']
                    )

            conn.commit()
            logger.info(f"Subproducto {subproducto['nombre']} producido x{cantidad_producida}")
            return subproducto

        except Exception as e:
            logger.error(f"Error produciendo subproducto: {e}")
            conn.rollback()
            raise
        finally: 
            conn.close()

    def eliminar_subproducto(self, subproducto_id):
        """Eliminar un subproducto."""
        conn = get_connection()
        if not conn:
            raise Exception("No database connection")

        try:
            with conn. cursor() as cursor:
                # Eliminar ingredientes primero
                cursor.execute(
                    "DELETE FROM subproducto_ingredientes WHERE subproducto_id = %s",
                    (subproducto_id,)
                )
                # Eliminar subproducto
                cursor.execute("DELETE FROM subproductos WHERE id = %s", (subproducto_id,))

            conn.commit()
            logger.info(f"Subproducto {subproducto_id} eliminado")

        except Exception as e:
            logger.error(f"Error eliminando subproducto: {e}")
            conn.rollback()
            raise
        finally: 
            conn.close()

    # ===== PRODUCTOS FINALES =====

    def get_productos_finales_info(self):
        """Obtener todos los productos finales con información de costos y precios."""
        conn = get_connection()
        if not conn: 
            return []

        try: 
            with conn.cursor() as cursor:
                sql = """
                    SELECT 
                        pf.id,
                        pf.nombre,
                        pf.unidades_producidas,
                        sp.costo_total_subproducto,
                        (sp.costo_total_subproducto / pf.unidades_producidas) AS costo_por_unidad
                    FROM productos_finales pf
                    JOIN subproductos sp ON pf.subproducto_id = sp.id
                    ORDER BY pf.nombre
                    """
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e: 
            logger.error(f"Error obteniendo productos finales:  {e}")
            return []
        finally:
            conn.close()

    def crear_producto_final(self, nombre, subproducto_id, unidades_producidas, precio_venta):
        """Crear un nuevo producto final."""
        conn = get_connection()
        if not conn:
            raise Exception("No database connection")

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO productos_finales "
                    "(nombre, subproducto_id, unidades_producidas, precio_venta) "
                    "VALUES (%s, %s, %s, %s)",
                    (nombre, subproducto_id, unidades_producidas, precio_venta)
                )

            conn.commit()
            logger.info(f"Producto final '{nombre}' creado")

        except Exception as e:
            logger.error(f"Error creando producto final: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def actualizar_producto_final(self, producto_id, precio_venta):
        """Actualizar precio de venta de un producto final."""
        conn = get_connection()
        if not conn:
            raise Exception("No database connection")

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE productos_finales SET precio_venta = %s WHERE id = %s",
                    (precio_venta, producto_id)
                )

            conn.commit()
            logger.info(f"Producto final {producto_id} actualizado")

        except Exception as e: 
            logger.error(f"Error actualizando producto final: {e}")
            conn.rollback()
            raise
        finally: 
            conn.close()

    def eliminar_producto_final(self, producto_id):
        """Eliminar un producto final."""
        conn = get_connection()
        if not conn:
            raise Exception("No database connection")

        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM productos_finales WHERE id = %s", (producto_id,))

            conn.commit()
            logger.info(f"Producto final {producto_id} eliminado")

        except Exception as e:
            logger.error(f"Error eliminando producto final: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()