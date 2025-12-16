from api.db.db_config import get_db_connection, DBError
from api import app

class Product:
    """Modelo para gestión de productos"""
    
    schema = {
        "name": str,
        "description": str,
        "price": (int, float),  
        "category_id": (int, type(None)),
    }

    @classmethod
    def validate(cls, data):
        """
        Valida los datos del producto.
        
        Args:
            data (dict): Datos a validar
            
        Returns:
            bool: True si los datos son válidos, False en caso contrario
        """
        if not isinstance(data, dict):
            return False
        
        for key, value_type in cls.schema.items():
            value = data.get(key)
            
            # Verifica que el tipo de dato coincida
            if key == "category_id":
                if value is not None and not isinstance(value, int):
                    return False
            else:
                if not isinstance(value, value_type):
                    return False
            
            # Validaciones adicionales
            if key == "name" and len(str(value).strip()) == 0:
                return False
                
            if key == "price" and value <= 0:
                return False
            
        return True

    def __init__(self, data):
        """Inicializa un objeto Product"""
        self._id = None 
        try:
            self._name = data["name"]
            self._price = data["price"]
            self._category_id = data["category_id"]
        except KeyError as e:
            raise ValueError(f"Falta la clave esperada: {e}")

    def to_json(self):
        """Convierte el producto a formato JSON"""
        return {
            "id": self._id,
            "name": self._name,
            "price": self._price,
            "category_id": self._category_id
        }

    @classmethod
    def get_products_by_user(cls, user_id):
        """
        Obtiene todos los productos de un usuario.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            list: Lista de productos en formato JSON
            
        Raises:
            DBError: Si no hay productos
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''SELECT p.id, p.name, p.description, p.price, p.category_id, 
                              c.name as category_name, 
                              COALESCE(s.quantity, 0) as stock_quantity
                       FROM products p
                       LEFT JOIN categories c ON p.category_id = c.id
                       LEFT JOIN stock s ON p.id = s.product_id
                       WHERE p.user_id = %s 
                       ORDER BY p.name''', 
                    (user_id,)
                )
                data = cursor.fetchall()

        if not data:
            raise DBError("No hay productos registrados")

        return [
            {
                "id": fila[0],
                "name": fila[1],
                "description": fila[2],
                "price": float(fila[3]),
                "category_id": fila[4],
                "category_name": fila[5],
                "stock_quantity": int(fila[6]) if fila[6] is not None else 0
            }
            for fila in data
        ]
        
    @classmethod
    def create_product(cls, user_id, data):
        """
        Crea un nuevo producto.
        
        Args:
            user_id (int): ID del usuario
            data (dict): Datos del producto
            
        Returns:
            tuple: Mensaje de éxito y código HTTP
            
        Raises:
            DBError: Si hay errores en la creación
        """
        name = data.get("name").strip()
        description = data.get("description", "").strip()
        price = data.get("price")
        category_id = data.get("category_id", None)
        
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    # Verificar si ya existe un producto con el mismo nombre
                    cursor.execute(
                        'SELECT id FROM products WHERE name = %s AND user_id = %s',
                        (name, user_id)
                    )
                    existing_product = cursor.fetchone()
                    if existing_product:
                        raise DBError("Ya existe un producto con ese nombre")

                    # Verificar si la categoría existe
                    if category_id is not None:
                        cursor.execute(
                            'SELECT id FROM categories WHERE id = %s AND user_id = %s', 
                            (category_id, user_id)
                        )
                        category_exists = cursor.fetchone()
                        if not category_exists:
                            raise DBError("La categoría especificada no existe")

                    # Crear producto
                    cursor.execute(
                        'INSERT INTO products (name, description, price, category_id, user_id) VALUES (%s, %s, %s, %s, %s)', 
                        (name, description, price, category_id if category_id else None, user_id)
                    )
                    connection.commit()

                except DBError as e:
                    raise DBError(f"Error al crear el producto: {str(e)}")
                except Exception as e:
                    raise DBError(f"Error interno del servidor: {str(e)}")

        return {"message": "Producto creado exitosamente"}, 201

    @classmethod
    def update_product(cls, user_id, product_id, data):
        """
        Actualiza un producto existente.
        
        Args:
            user_id (int): ID del usuario
            product_id (int): ID del producto
            data (dict): Nuevos datos del producto
            
        Returns:
            tuple: Mensaje de éxito y código HTTP
            
        Raises:
            DBError: Si hay errores en la actualización
        """
        name = data.get("name").strip()
        description = data.get("description", "").strip()
        price = data.get("price")
        category_id = data.get("category_id", None)

        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    # Verificar si el producto existe
                    cursor.execute(
                        'SELECT id FROM products WHERE id = %s AND user_id = %s',
                        (product_id, user_id)
                    )
                    if not cursor.fetchone():
                        raise DBError("El producto no existe")
                    
                    # Verificar si la categoría existe
                    if category_id is not None:
                        cursor.execute(
                            'SELECT id FROM categories WHERE id = %s AND user_id = %s', 
                            (category_id, user_id)
                        )
                        category_exists = cursor.fetchone()
                        if not category_exists:
                            raise DBError("La categoría especificada no existe")

                    cursor.execute(
                        'UPDATE products SET name = %s, description = %s, price = %s, category_id = %s WHERE id = %s AND user_id = %s',
                        (name, description, price, category_id, product_id, user_id)
                    )
                    connection.commit()

                except DBError as e:
                    raise DBError(f"Error al actualizar el producto: {str(e)}")

        return {"message": "Producto actualizado exitosamente"}, 200

    @classmethod
    def delete_product(cls, user_id, product_id):
        """
        Elimina un producto.
        
        Args:
            user_id (int): ID del usuario
            product_id (int): ID del producto
            
        Returns:
            tuple: Mensaje de éxito y código HTTP
            
        Raises:
            DBError: Si hay errores en la eliminación
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    # Verificar si el producto existe
                    cursor.execute(
                        'SELECT id FROM products WHERE id = %s AND user_id = %s', 
                        (product_id, user_id)
                    )
                    existing_product = cursor.fetchone()
                    if not existing_product:
                        raise DBError("El producto no existe")

                    # Eliminar el producto (el stock se elimina automáticamente por CASCADE)
                    cursor.execute(
                        'DELETE FROM products WHERE id = %s AND user_id = %s', 
                        (product_id, user_id)
                    )
                    connection.commit()

                except DBError as e:
                    raise DBError(f"Error al eliminar el producto: {str(e)}")

        return {"message": "Producto eliminado exitosamente"}, 200

    @classmethod
    def get_product_by_id(cls, user_id, product_id):
        """
        Obtiene un producto específico.
        
        Args:
            user_id (int): ID del usuario
            product_id (int): ID del producto
            
        Returns:
            dict: Datos del producto
            
        Raises:
            DBError: Si el producto no existe
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT id, name, price, category_id FROM products WHERE id = %s AND user_id = %s', 
                    (product_id, user_id)
                )
                data = cursor.fetchone()

        if not data:
            raise DBError("El producto no existe")

        return {
            "id": data[0],
            "name": data[1],
            "price": float(data[2]),
            "category_id": data[3]
        }

    @classmethod
    def get_products_by_category_id(cls, user_id, category_id):
        """
        Obtiene productos filtrados por categoría.
        
        Args:
            user_id (int): ID del usuario
            category_id (int): ID de la categoría (0 para sin categoría)
            
        Returns:
            list: Lista de productos
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Interpretar category_id igual a 0 como None
                if category_id == 0:
                    category_id = None

                if category_id is not None:
                    cursor.execute(
                        'SELECT id, name, price, category_id FROM products WHERE category_id = %s AND user_id = %s ORDER BY name',
                        (category_id, user_id)
                    )
                else:
                    cursor.execute(
                        'SELECT id, name, price, category_id FROM products WHERE category_id IS NULL AND user_id = %s ORDER BY name',
                        (user_id,)
                    )

                data = cursor.fetchall()

        return [
            {
                "id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "category_id": row[3]
            } for row in data
        ] if data else []
