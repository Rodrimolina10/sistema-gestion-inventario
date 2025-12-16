from api import app
from flask import request, jsonify
from api.models.user import User
from api.db.db_config import DBError

@app.route('/register', methods=['POST'])
def register():
    """
    Endpoint para registrar un nuevo usuario.
    
    Body (JSON):
    {
        "username": "string",
        "password": "string"
    }
    """
    data = request.get_json()
    try:
        response = User.register(data)
        return jsonify(response), 201  
    except Exception as e:
        if isinstance(e, DBError):
            info = e.args[0]
            return jsonify(info), info["code"]
        return jsonify({"message": str(e)}), 400
    
@app.route('/login', methods=['POST'])
def login():
    """
    Endpoint para iniciar sesión.
    
    Body (JSON):
    {
        "username": "string",
        "password": "string"
    }
    
    Returns:
    {
        "token": "JWT token",
        "username": "string",
        "user_id": int
    }
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username y password son requeridos"}), 400
    
    # Crear objeto auth compatible
    class Auth:
        def __init__(self, username, password):
            self.username = username
            self.password = password
    
    auth = Auth(data['username'], data['password'])
    
    try:
        user = User.login(auth)
        # Cambiar 'id' a 'user_id' para consistencia con el frontend
        return jsonify({
            "token": user["token"],
            "username": user["username"],
            "user_id": user["id"]
        }), 200
    except Exception as e:
        if isinstance(e, DBError):
            info = e.args[0]
            return jsonify({"error": info["message"]}), info["code"]
        return jsonify({"error": str(e)}), 400