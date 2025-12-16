from flask import request, jsonify
import jwt
from functools import wraps
from api import app
from api.db.db_config import get_db_connection, DBError

def token_required(func):
    """
    Decorador para proteger rutas que requieren autenticación JWT.
    
    Verifica:
    - Presencia del token en headers
    - Validez del token
    - Correspondencia entre user_id del token y el de la ruta
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None

        # Verificar si se incluye 'x-access-token' en los headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({"message": "Token de autenticación requerido"}), 401

        user_id = None
 
        # Verificar si 'user_id' está en los argumentos de la ruta
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']

        if user_id is None:
            # Si no está en la ruta, buscar en los headers
            if 'user_id' in request.headers:
                user_id = request.headers['user_id']

        if user_id is None:
            return jsonify({"message": "ID de usuario requerido"}), 401

        try:
            # Decodificar el token y validar
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            token_id = data['id']

            # Verificar que el user_id coincide con el del token
            if int(user_id) != int(token_id):
                return jsonify({"message": "Token inválido para este usuario"}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expirado. Por favor, inicia sesión nuevamente"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token inválido"}), 401
        except Exception as e:
            return jsonify({"message": f"Error de autenticación: {str(e)}"}), 401

        # Continuar con la ejecución de la función protegida
        return func(*args, **kwargs)
    
    return decorated

def optional_token(func):
    """
    Decorador para rutas donde el token es opcional.
    Si existe, lo valida; si no, permite el acceso.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        
        if token:
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                kwargs['current_user_id'] = data['id']
            except:
                pass
        
        return func(*args, **kwargs)
    
    return decorated
