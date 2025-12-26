import pymysql
from Core.database import get_connection
from Core.logger import setup_logger
from Core.produccion_backend import ProduccionBackend

logger = setup_logger()

class VentasBackend:
    def __init__(self):
        self.db = get_connection()
        self.prod_backend = ProduccionBackend() # To get product costs
        logger.info("VentasBackend initialized")

    def add_cliente(self, nombre_cliente):
        """Adds a new client to the database."""
        conn = get_connection()
        if not conn: raise Exception("No database connection")
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO clientes (nombre) VALUES (%s)", (nombre_cliente,))
            conn.commit()
            logger.info(f"Cliente '{nombre_cliente}' añadido.")
        except pymysql.IntegrityError:
            # This error happens if the client name already exists (due to UNIQUE constraint)
            logger.warning(f"El cliente '{nombre_cliente}' ya existe.")
            raise ValueError("Este cliente ya existe.")
        except Exception as e:
            logger.error(f"Error al añadir cliente: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_clientes(self, only_active=False):
        """Returns a list of clients. If only_active=True, filter active clients."""
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                # Check if 'active' column exists
                cursor.execute("SHOW COLUMNS FROM clientes LIKE 'active'")
                has_active = bool(cursor.fetchone())
                if has_active:
                    if only_active:
                        cursor.execute("SELECT id, nombre, active FROM clientes WHERE active = 1 ORDER BY nombre")
                    else:
                        cursor.execute("SELECT id, nombre, active FROM clientes ORDER BY nombre")
                else:
                    # Older DB without 'active' column -> assume active
                    cursor.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
                    rows = cursor.fetchall()
                    # normalize rows to include 'active' field = 1
                    return [{"id": r["id"], "nombre": r["nombre"], "active": 1} for r in rows]
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error al obtener clientes: {e}")
            return []
        finally:
            conn.close()

    def toggle_cliente_active(self, cliente_id):
        """Toggle active state for a client. Returns new state (1 or 0)."""
        conn = get_connection()
        if not conn: raise Exception("No database connection")
        try:
            with conn.cursor() as cursor:
                # ensure column exists
                cursor.execute("SHOW COLUMNS FROM clientes LIKE 'active'")
                if not cursor.fetchone():
                    # create column if missing (safe)
                    cursor.execute("ALTER TABLE clientes ADD COLUMN active TINYINT(1) NOT NULL DEFAULT 1")
                # Toggle
                cursor.execute("SELECT active FROM clientes WHERE id = %s", (cliente_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError("Cliente no encontrado")
                new_state = 0 if row.get("active", 1) == 1 else 1
                cursor.execute("UPDATE clientes SET active = %s WHERE id = %s", (new_state, cliente_id))
            conn.commit()
            return new_state
        except Exception as e:
            logger.error(f"Error toggling cliente active: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_clientes_activos(self):
        """Convenience wrapper to get active clients."""
        return self.get_clientes(only_active=True)

    def get_productos_con_costo(self):
        """
        Gets final products and adds their calculated cost for the sales UI.
        Also reads precio_venta from productos_finales if present.
        """
        productos_info = self.prod_backend.get_productos_finales_info()
        result = []
        conn = get_connection()
        try:
            for p in productos_info:
                pid = p.get("id")
                # get precio_venta from DB if available
                precio_venta = None
                try:
                    if conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT precio_venta FROM productos_finales WHERE id = %s", (pid,))
                            row = cursor.fetchone()
                            if row and row.get("precio_venta") is not None:
                                precio_venta = float(row.get("precio_venta") or 0)
                except Exception:
                    precio_venta = None

                try:
                    unidades_prod = float(p.get("unidades_producidas", 1)) if p.get("unidades_producidas") else 1.0
                except Exception:
                    unidades_prod = 1.0
                costo_total = float(p.get("costo_total_subproducto", 0) or 0)
                costo_unitario = round(costo_total / unidades_prod, 4) if unidades_prod else 0.0

                # Prefer precio_venta from DB; otherwise try from p dict, otherwise 0
                precio_venta_final = precio_venta if precio_venta is not None else float(p.get("precio_venta", 0) or 0)
                ganancia = round(precio_venta_final - costo_unitario, 4)
                ganancia_pct = round((ganancia / costo_unitario * 100), 2) if costo_unitario else None
                result.append({
                    "id": pid,
                    "nombre": p.get("nombre"),
                    "costo_total_subproducto": costo_total,
                    "unidades_producidas": unidades_prod,
                    "costo_unitario": costo_unitario,
                    "precio_venta": precio_venta_final,
                    "ganancia_unitaria": ganancia,
                    "ganancia_pct": ganancia_pct
                })
            return result
        finally:
            if conn:
                conn.close()

    def set_precio_venta(self, producto_final_id, precio):
        """
        Set or update the precio_venta for a producto_final.
        Adds the column if it doesn't exist (migration-safe).
        """
        conn = get_connection()
        if not conn: raise Exception("No database connection")
        try:
            with conn.cursor() as cursor:
                # Ensure column exists
                cursor.execute("SHOW COLUMNS FROM productos_finales LIKE 'precio_venta'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE productos_finales ADD COLUMN precio_venta DECIMAL(10,2) NULL DEFAULT NULL")
                cursor.execute("UPDATE productos_finales SET precio_venta = %s WHERE id = %s", (round(float(precio),2), producto_final_id))
            conn.commit()
            logger.info(f"Precio de venta actualizado: ProductoID {producto_final_id} -> {precio}")
        except Exception as e:
            logger.error(f"Error al setear precio de venta: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def registrar_venta(self, cliente_id, producto_final_id, cantidad_vendida, precio_unitario_venta):
        """
        Records a single sale transaction.
        """
        conn = get_connection()
        if not conn: raise Exception("No database connection")
        try:
            with conn.cursor() as cursor:
                # Calculate the total sale value
                total_venta = cantidad_vendida * precio_unitario_venta
                
                cursor.execute(
                    "INSERT INTO ventas (cliente_id, producto_final_id, cantidad_vendida, precio_unitario_venta, total_venta) VALUES (%s, %s, %s, %s, %s)",
                    (cliente_id, producto_final_id, cantidad_vendida, precio_unitario_venta, total_venta)
                )
            conn.commit()
            logger.info(f"Venta registrada: ClienteID {cliente_id}, ProductoID {producto_final_id}, Cantidad {cantidad_vendida}")
        except Exception as e:
            logger.error(f"Error al registrar venta: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def crear_venta_multiple(self, cliente_id, items):
        """
        Create a sale composed of multiple items.
        items: list of dicts: [{product_id, quantity, unit_price}, ...]
        We'll insert one row per item in ventas table inside a transaction.
        """
        if not items:
            raise ValueError("No hay items para registrar")
        conn = get_connection()
        if not conn: raise Exception("No database connection")
        try:
            total_venta = 0
            with conn.cursor() as cursor:
                # Optional: check cliente exists and active
                cursor.execute("SELECT id, COALESCE(active,1) as active FROM clientes WHERE id = %s", (cliente_id,))
                klient = cursor.fetchone()
                if not klient:
                    raise ValueError("Cliente no encontrado")
                if klient.get("active",1) != 1:
                    raise ValueError("Cliente inactivo. Activa el cliente antes de registrar ventas.")

                for it in items:
                    producto_id = it["product_id"]
                    cantidad = int(it.get("quantity", 1))
                    unit_price = float(it.get("unit_price", 0))
                    subtotal = round(cantidad * unit_price, 2)
                    total_venta += subtotal
                    cursor.execute(
                        "INSERT INTO ventas (cliente_id, producto_final_id, cantidad_vendida, precio_unitario_venta, total_venta) VALUES (%s, %s, %s, %s, %s)",
                        (cliente_id, producto_id, cantidad, unit_price, subtotal)
                    )
            conn.commit()
            logger.info(f"Venta multiple registrada para cliente {cliente_id}. Total: {total_venta}")
            return {"cliente_id": cliente_id, "total": total_venta}
        except Exception as e:
            logger.error(f"Error al crear venta multiple: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_cliente_stats(self, cliente_id):
        """Return purchases_count and total_revenue for a given client."""
        conn = get_connection()
        if not conn: return {"purchases_count": 0, "total_revenue": 0.0}
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS cnt, COALESCE(SUM(total_venta),0) AS total FROM ventas WHERE cliente_id = %s", (cliente_id,))
                row = cursor.fetchone() or {"cnt": 0, "total": 0}
                return {"purchases_count": int(row.get("cnt", 0)), "total_revenue": float(row.get("total", 0.0))}
        except Exception as e:
            logger.error(f"Error en get_cliente_stats: {e}")
            return {"purchases_count": 0, "total_revenue": 0.0}
        finally:
            conn.close()

    def get_ventas_por_dia(self, cliente_id):
        """
        Returns list grouped by day:
        [{day: 'YYYY-MM-DD', sales_count: n, total_sum: x.xx}, ...]
        """
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT DATE(fecha_venta) AS dia, COUNT(*) AS ventas_count, COALESCE(SUM(total_venta),0) AS total_sum
                    FROM ventas
                    WHERE cliente_id = %s
                    GROUP BY dia
                    ORDER BY dia DESC
                """
                cursor.execute(sql, (cliente_id,))
                rows = cursor.fetchall()
                return [{"day": str(r["dia"]), "sales_count": int(r["ventas_count"]), "total_sum": float(r["total_sum"])} for r in rows]
        except Exception as e:
            logger.error(f"Error en get_ventas_por_dia: {e}")
            return []
        finally:
            conn.close()

    def get_historial_ventas(self):
        """Returns the full sales history with client and product names."""
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT
                    v.id,
                    v.fecha_venta,
                    c.nombre AS cliente,
                    pf.nombre AS producto,
                    v.cantidad_vendida,
                    v.precio_unitario_venta,
                    v.total_venta
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                LEFT JOIN productos_finales pf ON v.producto_final_id = pf.id
                ORDER BY v.fecha_venta DESC
                """
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error al obtener historial de ventas: {e}")
            return []
        finally:
            conn.close()