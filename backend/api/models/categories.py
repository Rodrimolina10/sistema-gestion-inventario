from api.db.db_config import get_db_connection, DBError
from api import app

class Category:
    """Modelo para gestión de categorías de productos"""
    
    schema = {
        "name": str,
        "descripcion": str  
    }

    @classmethod
    def validate(cls, data):
        """
        Valida los datos de la categoría.
        
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
        
        # Validaciones adicionales
        if len(data["name"].strip()) == 0:
            return False
            
        return True

    def __init__(self, data):
        """Inicializa un objeto Category"""
        self._id = data[0]
        self._name = data[1]
        self._descripcion = data[2]  

    def to_json(self):
        """Convierte la categoría a formato JSON"""
        return {
            "id": self._id,
            "name": self._name,
            "descripcion": self._descripcion,
        }

    @classmethod
    def get_categories(cls, user_id):
        """
        Obtiene todas las categorías para un usuario.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            list: Lista de categorías en formato JSON
            
        Raises:
            DBError: Si no hay categorías
        """
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM categories WHERE user_id = %s ORDER BY name', 
                         (user_id,))
            data = cursor.fetchall()

            if not data:
                raise DBError("No hay categorías registradas")

            return [cls(fila).to_json() for fila in data]

    @classmethod
    def create_category(cls, user_id, data):
        """
        Crea una nueva categoría para un usuario.
        
        Args:
            user_id (int): ID del usuario
            data (dict): Datos de la categoría
            
        Returns:
            tuple: Mensaje de éxito y código HTTP
            
        Raises:
            DBError: Si hay errores en la creación
        """
        name = data.get("name").strip()
        descripcion = data.get("descripcion").strip()

        with get_db_connection() as connection:
            cursor = connection.cursor()
            try:
                # Verificar si el usuario existe
                cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
                user = cursor.fetchone()
                if not user:
                    raise DBError("El usuario no existe")

                # Verificar si ya existe una categoría con ese nombre
                cursor.execute(
                    'SELECT id FROM categories WHERE name = %s AND user_id = %s', 
                    (name, user_id)
                )
                existing_category = cursor.fetchone()
                if existing_category:
                    raise DBError("Ya existe una categoría con ese nombre")

                # Insertar la nueva categoría
                cursor.execute(
                    'INSERT INTO categories (name, descripcion, user_id) VALUES (%s, %s, %s)', 
                    (name, descripcion, user_id)
                )
                connection.commit()

            except Exception as e:
                raise DBError(f"Error al crear la categoría: {str(e)}")

        return {"message": "Categoría creada exitosamente"}, 201

    @classmethod
    def update_category(cls, user_id, category_id, data):
        """
        Actualiza una categoría existente.
        
        Args:
            user_id (int): ID del usuario
            category_id (int): ID de la categoría
            data (dict): Nuevos datos de la categoría
            
        Returns:
            tuple: Mensaje de éxito y código HTTP
            
        Raises:
            DBError: Si hay errores en la actualización
        """
        name = data.get("name").strip()
        descripcion = data.get("descripcion").strip()

        with get_db_connection() as connection:
            cursor = connection.cursor()
            try:
                # Verificar si la categoría existe para el usuario
                cursor.execute(
                    'SELECT id FROM categories WHERE id = %s AND user_id = %s', 
                    (category_id, user_id)
                )
                existing_category = cursor.fetchone()
                if not existing_category:
                    raise DBError("La categoría no existe para este usuario")

                # Actualizar la categoría
                cursor.execute(
                    'UPDATE categories SET name = %s, descripcion = %s WHERE id = %s AND user_id = %s',
                    (name, descripcion, category_id, user_id)
                )
                connection.commit()

            except Exception as e:
                raise DBError(f"Error al actualizar la categoría: {str(e)}")

        return {"message": "Categoría actualizada exitosamente"}, 200

    @classmethod
    def delete_category(cls, user_id, category_id):
        """
        Elimina una categoría para un usuario.
        
        Args:
            user_id (int): ID del usuario
            category_id (int): ID de la categoría
            
        Returns:
            tuple: Mensaje de éxito y código HTTP
            
        Raises:
            DBError: Si hay errores en la eliminación
        """
        with get_db_connection() as connection:
            cursor = connection.cursor()
            try:
                # Verificar si la categoría existe
                cursor.execute(
                    'SELECT id FROM categories WHERE id = %s AND user_id = %s', 
                    (category_id, user_id)
                )
                existing_category = cursor.fetchone()
                if not existing_category:
                    raise DBError("La categoría no existe para este usuario")

                # Actualizar los productos para desvincularlos de la categoría eliminada
                cursor.execute(
                    'UPDATE products SET category_id = NULL WHERE category_id = %s AND user_id = %s',
                    (category_id, user_id)
                )

                # Eliminar la categoría
                cursor.execute(
                    'DELETE FROM categories WHERE id = %s AND user_id = %s', 
                    (category_id, user_id)
                )
                connection.commit()

            except Exception as e:
                connection.rollback()
                raise DBError(f"Error al eliminar la categoría: {str(e)}")

        return {"message": "Categoría eliminada exitosamente"}, 200
