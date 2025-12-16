from api.db.db_config import get_db_connection, DBError
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from api import app
import re

app.config['SECRET_KEY'] = "clave_app_segura_2024"

class User:
    """Modelo para gestión de usuarios del sistema"""
    
    schema = {
        "username": str,
        "password": str
    }

    @classmethod
    def validate(cls, data):
        """
        Valida los datos del usuario.
        
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
        
        # Validación de username
        username = data.get("username", "")
        if len(username) < 3 or len(username) > 50:
            return False
        
        # Validación de password
        password = data.get("password", "")
        if len(password) < 6:
            return False
            
        return True
    
    def __init__(self, data):
        """Inicializa un objeto User"""
        self._id = data[0]
        self._username = data[1]
        self._password = data[2]

    def to_json(self):
        """Convierte el usuario a formato JSON"""
        return {
            "id": self._id,
            "username": self._username
        } 
    
    @classmethod
    def register(cls, data):
        """
        Registra un nuevo usuario en el sistema.
        
        Args:
            data (dict): Datos del usuario (username, password)
            
        Returns:
            dict: Datos del usuario creado
            
        Raises:
            DBError: Si hay errores en la validación o creación
        """
        if not cls.validate(data):
            raise DBError({"message": "Campos/valores inválidos. El username debe tener entre 3 y 50 caracteres y la contraseña al menos 6 caracteres.", "code": 400})
        
        username = data["username"].strip()
        password = data["password"]

        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            # Verificar si existe un usuario con el mismo nombre
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            row = cursor.fetchone()
            
            if row is not None:
                raise DBError({"message": "Ya existe un usuario con ese nombre", "code": 400})
            
            # Generar el hash de la contraseña
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Guardar el usuario en la base de datos
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', 
                         (username, hashed_password))
            connection.commit()
            
            # Obtener el id del registro creado
            cursor.execute('SELECT LAST_INSERT_ID()')
            row = cursor.fetchone()
            user_id = row[0]

            # Recuperar el objeto creado
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            nuevo = cursor.fetchone()
            
            return User(nuevo).to_json()
            
        except DBError:
            raise
        except Exception as e:
            raise DBError({"message": f"Error al registrar usuario: {str(e)}", "code": 500})
        finally:
            cursor.close()
            connection.close()
    
    @classmethod
    def login(cls, auth):
        """
        Autentica un usuario y genera un token JWT.
        
        Args:
            auth: Objeto con credenciales (username, password)
            
        Returns:
            dict: Token JWT y datos del usuario
            
        Raises:
            DBError: Si las credenciales son inválidas
        """
        if not auth or not auth.username or not auth.password:
            raise DBError({"message": "Credenciales incompletas", "code": 401})

        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            # Buscar el usuario por nombre de usuario
            cursor.execute('SELECT id, username, password FROM users WHERE username = %s', 
                         (auth.username,))
            row = cursor.fetchone()

            # Verificar contraseña
            if not row or not check_password_hash(row[2], auth.password): 
                raise DBError({"message": "Usuario o contraseña incorrectos", "code": 401})

            # Generar token JWT con expiración de 12 horas
            exp_timestamp = (datetime.datetime.now(datetime.timezone.utc) + 
                           datetime.timedelta(hours=12)).timestamp()
            
            token = jwt.encode({
                'username': auth.username,
                'id': row[0],
                'exp': exp_timestamp
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            return {
                "token": token, 
                "username": auth.username, 
                "id": row[0]
            }
            
        finally:
            cursor.close()
            connection.close()
