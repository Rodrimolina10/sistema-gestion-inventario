from api.db.db_config import get_db_connection, DBError
from flask import request, jsonify
from api import app
import datetime

class Order:
    """Modelo para gestión de órdenes de compra"""
    
    schema = {
        "products": list
    }

    @classmethod
    def validate(cls, data):
        """
        Valida los datos de la orden.
        
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
        
        # Validar que hay al menos un producto
        if len(data["products"]) == 0:
            return False
        
        # Validar estructura de cada producto
        for product in data["products"]:
            if not isinstance(product, dict):
                return False
            if "product_id" not in product or "quantity" not in product:
                return False
            if not isinstance(product["product_id"], int) or not isinstance(product["quantity"], int):
                return False
            if product["quantity"] <= 0:
                return False
                
        return True

    def __init__(self, data):
        """
        Inicializa un objeto Order.
        
        Args:
            data (dict): Diccionario con los datos de la orden
        """
        self.id = data.get("id")
        self.order_date = data.get("order_date")
        self.received_date = data.get("received_date")
        self.status = data.get("status", 'pending')
        self.products = data.get("products", [])

    def to_json(self):
        """Convierte el objeto Order a formato JSON"""
        return {
            "id": self.id,
            "order_date": str(self.order_date) if self.order_date else None,
            "received_date": str(self.received_date) if self.received_date else None,
            "status": self.status,
            "products": self.products
        }

    @classmethod
    def get_orders_by_user(cls, user_id, status_filter=None):
        """
        Obtiene todas las órdenes de un usuario.
        
        Args:
            user_id (int): ID del usuario
            status_filter (str): Filtro opcional por estado
            
        Returns:
            list: Lista de órdenes
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                if status_filter:
                    cursor.execute(
                        'SELECT * FROM purchase_orders WHERE user_id = %s AND status = %s ORDER BY order_date DESC',
                        (user_id, status_filter)
                    )
                else:
                    cursor.execute(
                        'SELECT * FROM purchase_orders WHERE user_id = %s ORDER BY order_date DESC',
                        (user_id,)
                    )
                orders = cursor.fetchall()
                
                result = []
                for order in orders:
                    cursor.execute(
                        'SELECT * FROM order_products WHERE order_id = %s',
                        (order[0],)
                    )
                    products = cursor.fetchall()
                    result.append({
                        "id": order[0],
                        "order_date": str(order[1]),
                        "received_date": str(order[2]) if order[2] else None,
                        "status": order[3],
                        "products": [
                            {
                                "product_id": product[2],
                                "quantity": product[3]
                            } for product in products
                        ]
                    })
        return result

    @classmethod
    def create_order(cls, user_id, data):
        """
        Crea una nueva orden de compra.
        
        Args:
            user_id (int): ID del usuario
            data (dict): Datos de la orden
            
        Returns:
            tuple: Mensaje de éxito y código HTTP
            
        Raises:
            DBError: Si hay errores en la creación
        """
        products = data.get("products")

        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    # Verificar que todos los productos existen
                    for product in products:
                        cursor.execute(
                            'SELECT id FROM products WHERE id = %s AND user_id = %s',
                            (product["product_id"], user_id)
                        )
                        if not cursor.fetchone():
                            raise DBError(f"El producto con ID {product['product_id']} no existe")

                    # Crear la orden en purchase_orders
                    cursor.execute(
                        'INSERT INTO purchase_orders (user_id) VALUES (%s)',
                        (user_id,)
                    )
                    order_id = cursor.lastrowid
                    
                    # Insertar los productos de la orden
                    for product in products:
                        cursor.execute(
                            'INSERT INTO order_products (order_id, product_id, quantity) VALUES (%s, %s, %s)',
                            (order_id, product["product_id"], product["quantity"])
                        )
                    connection.commit()

                    return {"message": "Orden creada exitosamente", "order_id": order_id}, 201

                except Exception as e:
                    connection.rollback()
                    raise DBError(f"Error al crear la orden: {e}")

    @classmethod
    def update_order(cls, user_id, order_id, received_date=None):
        """
        Actualiza una orden a estado 'completed'.
        
        Args:
            user_id (int): ID del usuario
            order_id (int): ID de la orden
            received_date (str): Fecha de recepción opcional
            
        Returns:
            tuple: Mensaje de éxito y código HTTP
            
        Raises:
            DBError: Si hay errores en la actualización
        """
        new_status = 'completed'
        received_date = received_date or datetime.date.today().strftime('%Y-%m-%d')

        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    # Verificar estado actual
                    cursor.execute(
                        'SELECT status FROM purchase_orders WHERE id = %s AND user_id = %s',
                        (order_id, user_id)
                    )
                    current_status = cursor.fetchone()
                    if not current_status:
                        raise DBError("La orden no existe")
                    if current_status[0] != 'pending':
                        raise DBError("Solo se pueden completar órdenes pendientes")

                    # Obtener productos de la orden
                    cursor.execute(
                        'SELECT product_id, quantity FROM order_products WHERE order_id = %s',
                        (order_id,)
                    )
                    products = cursor.fetchall()
                    if not products:
                        raise DBError("No se encontraron productos para esta orden")

                    # Actualizar stock para cada producto
                    for product_id, quantity in products:
                        cursor.execute(
                            'SELECT quantity FROM stock WHERE product_id = %s AND user_id = %s',
                            (product_id, user_id)
                        )
                        current_stock = cursor.fetchone()
                        if not current_stock:
                            raise DBError(f"El producto {product_id} no tiene stock asociado")

                        new_quantity = current_stock[0] + quantity
                        cursor.execute(
                            'UPDATE stock SET quantity = %s WHERE product_id = %s AND user_id = %s',
                            (new_quantity, product_id, user_id)
                        )

                    # Actualizar estado de la orden
                    cursor.execute(
                        'UPDATE purchase_orders SET status = %s, received_date = %s WHERE id = %s AND user_id = %s',
                        (new_status, received_date, order_id, user_id)
                    )

                    connection.commit()
                    return {"message": "Orden completada y stock actualizado exitosamente"}, 200

                except Exception as e:
                    connection.rollback()
                    raise DBError(f"Error al actualizar la orden: {e}")

    @classmethod
    def delete_order(cls, user_id, order_id):
        """
        Elimina (marca como eliminada) una orden.
        
        Args:
            user_id (int): ID del usuario
            order_id (int): ID de la orden
            
        Returns:
            tuple: Mensaje de éxito y código HTTP
            
        Raises:
            DBError: Si hay errores en la eliminación
        """
        new_status = 'deleted'
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    # Verificar estado de la orden
                    cursor.execute(
                        'SELECT status FROM purchase_orders WHERE id = %s AND user_id = %s',
                        (order_id, user_id)
                    )
                    order_status = cursor.fetchone()

                    if not order_status:
                        raise DBError("La orden no existe")

                    if order_status[0] != 'pending':
                        raise DBError("Solo se pueden eliminar órdenes pendientes")

                    # Cambiar estado a 'deleted'
                    cursor.execute(
                        'UPDATE purchase_orders SET status = %s WHERE id = %s AND user_id = %s',
                        (new_status, order_id, user_id)
                    )
                    connection.commit()

                    return {"message": "Orden eliminada exitosamente"}, 200

                except Exception as e:
                    connection.rollback()
                    raise DBError(f"Error al eliminar la orden: {e}")

    @classmethod
    def get_order_by_id(cls, user_id, order_id):
        """
        Obtiene una orden específica.
        
        Args:
            user_id (int): ID del usuario
            order_id (int): ID de la orden
            
        Returns:
            dict: Datos de la orden
            
        Raises:
            DBError: Si la orden no existe
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT * FROM purchase_orders WHERE id = %s AND user_id = %s',
                    (order_id, user_id)
                )
                order = cursor.fetchone()
                if not order:
                    raise DBError("La orden no existe")

                cursor.execute(
                    'SELECT * FROM order_products WHERE order_id = %s',
                    (order_id,)
                )
                products = cursor.fetchall()

        return {
            "id": order[0],
            "order_date": str(order[1]),
            "received_date": str(order[2]) if order[2] else None,
            "status": order[3],
            "products": [
                {
                    "product_id": product[2],
                    "quantity": product[3]
                } for product in products
            ]
        }
