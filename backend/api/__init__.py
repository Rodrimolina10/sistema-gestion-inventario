from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de la aplicación
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_app_segura_2024')
app.config['JSON_AS_ASCII'] = False  # Soporte para UTF-8

@app.route('/')
def index():
    """Ruta de verificación del servidor"""
    return jsonify({
        "message": "✅ Sistema de Gestión de Inventario - API funcionando correctamente",
        "version": "2.0",
        "status": "online"
    })

@app.route('/health')
def health_check():
    """Ruta para verificar el estado del servidor"""
    return jsonify({
        "status": "healthy",
        "service": "Inventory Management API"
    }), 200

# Importar rutas (después de crear la app)
import api.routes.user
import api.routes.products
import api.routes.categories
import api.routes.stock
import api.routes.supplier
import api.routes.orders
import api.routes.reports

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Método no permitido"}), 405
