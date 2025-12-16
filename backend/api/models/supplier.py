from api.db.db_config import get_db_connection, DBError
from flask import request, jsonify
from api import app
import re

class Supplier:
    """Modelo para gestión de proveedores"""
    
    schema = {
        "name_supplier": str,
        "phone": str,
        "mail": str
    }

    @classmethod
    def validate(cls, data):
        """
        Valida los datos del proveedor.
        
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
        if len(data["name_supplier"].strip()) == 0:
            return False
        
        # Validar formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data["mail"]):
            return False
            
        return True

    def __init__(self, data):
        """
        Inicializa un objeto Supplier.
        
        Args:
            data (tuple): Tupla con (id, name_supplier, phone, mail)
        """
        self.id = data[0]
        self.name_supplier = data[1]
        self.phone = data[2]
        self.mail = data[3]
    
    def to_json(self):
        """Convierte el objeto Supplier a formato JSON"""
        return {
            "id": self.id,
            "name_supplier": self.name_supplier,
            "phone": self.phone,
            "mail": self.mail,
        }

    @classmethod
    def create_supplier(cls, user_id, data):
        """
        Crea un nuevo proveedor asociado a un usuario.
        
        Args:
            user_id (int): ID del usuario
            data (dict): Datos del proveedor
            
        Returns:
            dict: Proveedor creado en formato JSON
            
        Raises:
            DBError: Si hay errores en la creación
        """
        if not cls.validate(data):
            raise DBError("Campos/valores inválidos. Verifica el formato del email.")

        connection = get_db_connection()
        cursor = connection.cursor()

        name_supplier = data["name_supplier"].strip()
        phone = data["phone"].strip()
        mail = data["mail"].strip().lower()

        try:
            # Verificar que el proveedor no existe
            cursor.execute(
                'SELECT id FROM suppliers WHERE name_supplier = %s AND user_id = %s',
                (name_supplier, user_id)
            )
            if cursor.fetchone():
                raise DBError("Ya existe un proveedor con ese nombre")

            # Verificar que el teléfono no está registrado
            cursor.execute(
                'SELECT id FROM suppliers WHERE phone = %s AND user_id = %s',
                (phone, user_id)
            )
            if cursor.fetchone():
                raise DBError("El número de teléfono ya está registrado")

            # Verificar que el correo no está registrado
            cursor.execute(
                'SELECT id FROM suppliers WHERE mail = %s AND user_id = %s',
                (mail, user_id)
            )
            if cursor.fetchone():
                raise DBError("El correo electrónico ya está registrado")

            # Insertar proveedor
            cursor.execute(
                '''INSERT INTO suppliers (name_supplier, phone, mail, user_id) 
                   VALUES (%s, %s, %s, %s)''',
                (name_supplier, phone, mail, user_id)
            )
            connection.commit()

            # Obtener ID del proveedor recién creado
            cursor.execute('SELECT LAST_INSERT_ID()')
            supplier_id = cursor.fetchone()[0]

            # Recuperar y devolver el proveedor creado
            cursor.execute('SELECT * FROM suppliers WHERE id = %s', (supplier_id,))
            nuevo = cursor.fetchone()

            return Supplier(nuevo).to_json()
            
        except DBError:
            raise
        except Exception as e:
            connection.rollback()
            raise DBError(f"Error creando el proveedor: {e}")
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def add_product_to_supplier(cls, user_id, supplier_id, product_id):
        """
        Asocia un producto a un proveedor.
        
        Args:
            user_id (int): ID del usuario autenticado
            supplier_id (int): ID del proveedor
            product_id (int): ID del producto
            
        Raises:
            DBError: Si hay errores en la asociación
        """
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Verificar que el proveedor existe y pertenece al usuario
            cursor.execute(
                'SELECT id FROM suppliers WHERE id = %s AND user_id = %s',
                (supplier_id, user_id)
            )
            if not cursor.fetchone():
                raise DBError("El proveedor no existe o no pertenece al usuario")

            # Verificar que el producto existe y pertenece al usuario
            cursor.execute(
                'SELECT id FROM products WHERE id = %s AND user_id = %s',
                (product_id, user_id)
            )
            if not cursor.fetchone():
                raise DBError("El producto no existe o no pertenece al usuario")

            # Verificar que la asociación no existe ya
            cursor.execute(
                '''SELECT supplier_id FROM suppliers_products 
                   WHERE supplier_id = %s AND product_id = %s AND user_id = %s''',
                (supplier_id, product_id, user_id)
            )
            if cursor.fetchone():
                raise DBError("El producto ya está asociado al proveedor")

            # Asociar el producto al proveedor
            cursor.execute(
                '''INSERT INTO suppliers_products (supplier_id, product_id, user_id) 
                   VALUES (%s, %s, %s)''',
                (supplier_id, product_id, user_id)
            )
            connection.commit()

        except DBError:
            raise
        except Exception as e:
            connection.rollback()
            raise DBError(f"Error asociando producto: {e}")
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def get_suppliers_by_product(cls, user_id, product_id):
        """
        Obtiene proveedores asociados a un producto específico.
        
        Args:
            user_id (int): ID del usuario autenticado
            product_id (int): ID del producto
            
        Returns:
            list o dict: Lista de proveedores o mensaje
            
        Raises:
            DBError: Si hay errores en la consulta
        """
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Verificar que el producto pertenece al usuario
            cursor.execute(
                'SELECT id FROM products WHERE id = %s AND user_id = %s',
                (product_id, user_id)
            )
            if not cursor.fetchone():
                raise DBError("Producto no encontrado o no pertenece al usuario")

            # Obtener proveedores asociados
            cursor.execute(
                '''SELECT suppliers.id, suppliers.name_supplier, suppliers.phone, 
                          suppliers.mail, suppliers.user_id 
                   FROM suppliers
                   JOIN suppliers_products ON suppliers.id = suppliers_products.supplier_id
                   WHERE suppliers_products.product_id = %s AND suppliers.user_id = %s
                   ORDER BY suppliers.name_supplier''',
                (product_id, user_id)
            )
            suppliers = cursor.fetchall()

            if not suppliers:
                return {"message": "No hay proveedores asociados a este producto"}

            return [
                {
                    "id": i[0],
                    "name_supplier": i[1],
                    "phone": i[2],
                    "mail": i[3],
                    "user_id": i[4]
                }
                for i in suppliers
            ]

        except DBError:
            raise
        except Exception as e:
            raise DBError(f"Error obteniendo proveedores: {e}")
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def get_suppliers_by_user(cls, user_id):
        """
        Obtiene todos los proveedores de un usuario.
        
        Args:
            user_id (int): ID del usuario autenticado
            
        Returns:
            list o dict: Lista de proveedores o mensaje
            
        Raises:
            DBError: Si hay errores en la consulta
        """
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                '''SELECT id, name_supplier, phone, mail 
                   FROM suppliers 
                   WHERE user_id = %s
                   ORDER BY name_supplier''',
                (user_id,)
            )
            suppliers = cursor.fetchall()

            if suppliers:
                return [
                    {
                        "id": row[0], 
                        "name_supplier": row[1],
                        "phone": row[2],
                        "mail": row[3]
                    }
                    for row in suppliers
                ]
            
            return {"message": "No hay proveedores asociados a este usuario"}
            
        except Exception as e:
            raise DBError(f"Error obteniendo proveedores: {e}")
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def delete_supplier(cls, user_id, supplier_id):
        """
        Elimina un proveedor.
        
        Args:
            user_id (int): ID del usuario
            supplier_id (int): ID del proveedor
            
        Returns:
            tuple: Mensaje de éxito y código HTTP
            
        Raises:
            DBError: Si hay errores en la eliminación
        """
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Verificar que el proveedor existe
            cursor.execute(
                'SELECT id FROM suppliers WHERE id = %s AND user_id = %s',
                (supplier_id, user_id)
            )
            if not cursor.fetchone():
                raise DBError("El proveedor no existe")

            # Eliminar proveedor (las relaciones se eliminan por CASCADE)
            cursor.execute(
                'DELETE FROM suppliers WHERE id = %s AND user_id = %s',
                (supplier_id, user_id)
            )
            connection.commit()

            return {"message": "Proveedor eliminado exitosamente"}, 200

        except DBError:
            raise
        except Exception as e:
            connection.rollback()
            raise DBError(f"Error eliminando proveedor: {e}")
        finally:
            cursor.close()
            connection.close()
