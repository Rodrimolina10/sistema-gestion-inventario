from api.db.db_config import get_db_connection, DBError
from api import app

class Stock:
    """Modelo para gestión de inventario"""
    
    # Umbral predeterminado para alertas de bajo stock (modificado de 10 a 5)
    DEFAULT_LOW_STOCK_THRESHOLD = 5
    
    schema = {
        "quantity": int
    }

    @classmethod
    def validate(cls, data):
        """
        Valida que los datos contengan solo 'quantity'.
        
        Args:
            data (dict): Datos a validar
            
        Returns:
            bool: True si los datos son válidos, False en caso contrario
        """
        if data is None or not isinstance(data, dict):
            return False

        for key in cls.schema:
            if key not in data:
                return False
            if not isinstance(data[key], cls.schema[key]):
                return False

        # Validar que la cantidad sea positiva
        if data["quantity"] < 0:
            return False

        return True

    def __init__(self, data):
        """
        Inicializa un objeto Stock.
        
        Args:
            data (tuple): Tupla con (product_id, product_name, quantity)
        """
        self.product_id = data[0]
        self.product_name = data[1]
        self.quantity = data[2]

    def to_json(self):
        """Convierte el objeto Stock a formato JSON"""
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity
        }

    @classmethod
    def update_stock(cls, user_id, product_id, new_quantity):
        """
        Actualiza la cantidad de productos en stock.
        
        Args:
            user_id (int): ID del usuario autenticado
            product_id (int): ID del producto
            new_quantity (int): Nueva cantidad para el producto
            
        Returns:
            dict: Mensaje indicando el resultado
            
        Raises:
            DBError: Si hay errores en la actualización
        """
        if new_quantity < 0:
            raise DBError("La cantidad no puede ser negativa")

        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            # Verificar que el producto existe y pertenece al usuario
            cursor.execute(
                'SELECT quantity FROM stock WHERE product_id = %s AND user_id = %s',
                (product_id, user_id)
            )
            current_quantity = cursor.fetchone()
            
            if not current_quantity:
                raise DBError("El producto no existe o no pertenece al usuario")
            
            if current_quantity[0] == new_quantity:
                return {"message": "Stock no actualizado, la cantidad es la misma"}
            
            # Actualizar stock
            cursor.execute(
                'UPDATE stock SET quantity = %s WHERE product_id = %s AND user_id = %s',
                (new_quantity, product_id, user_id)
            )
            
            connection.commit()
            
            # Verificar si el stock está bajo
            warning = ""
            if new_quantity <= cls.DEFAULT_LOW_STOCK_THRESHOLD:
                warning = f" ⚠️ ALERTA: Stock bajo (≤{cls.DEFAULT_LOW_STOCK_THRESHOLD} unidades)"
            
            return {"message": f"Stock actualizado exitosamente{warning}"}
            
        except DBError:
            raise
        except Exception as e:
            connection.rollback()
            raise DBError(f"Error actualizando el stock: {e}")
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def check_low_stock(cls, user_id, threshold=None):
        """
        Verifica productos con stock bajo.
        
        Args:
            user_id (int): ID del usuario autenticado
            threshold (int): Umbral personalizado (por defecto 5)
            
        Returns:
            list o dict: Lista de productos con stock bajo o mensaje
            
        Raises:
            DBError: Si hay errores en la consulta
        """
        if threshold is None:
            threshold = cls.DEFAULT_LOW_STOCK_THRESHOLD

        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                '''SELECT stock.product_id, products.name, stock.quantity 
                   FROM stock 
                   JOIN products ON stock.product_id = products.id 
                   WHERE stock.quantity <= %s AND stock.user_id = %s
                   ORDER BY stock.quantity ASC, products.name''',
                (threshold, user_id)
            )
            data = cursor.fetchall()

            if data:
                low_stock_products = [Stock(row).to_json() for row in data]
                return {
                    "data": low_stock_products,
                    "threshold": threshold,
                    "count": len(low_stock_products)
                }
            
            return {
                "message": "No hay productos con stock bajo",
                "threshold": threshold
            }
            
        except Exception as e:
            raise DBError(f"Error verificando stock bajo: {e}")
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def get_stock_by_user(cls, user_id):
        """
        Obtiene el stock de todos los productos de un usuario.
        
        Args:
            user_id (int): ID del usuario autenticado
            
        Returns:
            list o dict: Lista de productos en stock o mensaje
            
        Raises:
            DBError: Si hay errores en la consulta
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                SELECT stock.product_id, products.name, stock.quantity
                FROM stock 
                JOIN products ON stock.product_id = products.id
                WHERE stock.user_id = %s
                ORDER BY products.name
            ''', (user_id,))
            
            data = cursor.fetchall()

            if data:
                all_stock = [
                    {
                        "product_id": row[0],
                        "product_name": row[1],
                        "quantity": row[2],
                        "low_stock": row[2] <= cls.DEFAULT_LOW_STOCK_THRESHOLD
                    }
                    for row in data
                ]
                return all_stock
            
            return {"message": "No hay productos en stock"}
            
        except Exception as e:
            raise DBError(f"Error obteniendo el stock: {e}")
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def get_stock_statistics(cls, user_id):
        """
        Obtiene estadísticas del inventario.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            dict: Estadísticas del stock
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            # Total de productos
            cursor.execute(
                'SELECT COUNT(*) FROM stock WHERE user_id = %s',
                (user_id,)
            )
            total_products = cursor.fetchone()[0]
            
            # Total de unidades
            cursor.execute(
                'SELECT SUM(quantity) FROM stock WHERE user_id = %s',
                (user_id,)
            )
            total_units = cursor.fetchone()[0] or 0
            
            # Productos con stock bajo
            cursor.execute(
                'SELECT COUNT(*) FROM stock WHERE user_id = %s AND quantity <= %s',
                (user_id, cls.DEFAULT_LOW_STOCK_THRESHOLD)
            )
            low_stock_count = cursor.fetchone()[0]
            
            # Productos sin stock
            cursor.execute(
                'SELECT COUNT(*) FROM stock WHERE user_id = %s AND quantity = 0',
                (user_id,)
            )
            out_of_stock = cursor.fetchone()[0]
            
            return {
                "total_products": total_products,
                "total_units": total_units,
                "low_stock_count": low_stock_count,
                "out_of_stock": out_of_stock,
                "low_stock_threshold": cls.DEFAULT_LOW_STOCK_THRESHOLD
            }
            
        except Exception as e:
            raise DBError(f"Error obteniendo estadísticas: {e}")
        finally:
            cursor.close()
            connection.close()
