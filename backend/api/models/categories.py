from api import app
from flask import request, jsonify
from api.db.db_config import get_db_connection

# RUTAS DE CATEGORÍAS

@app.route('/usuario/<int:user_id>/clasificaciones', methods=['GET', 'OPTIONS'])
def obtener_clasificaciones(user_id):
    """Obtiene todas las categorías de un usuario"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT id, name, descripcion,
                   (SELECT COUNT(*) FROM products WHERE category_id = categories.id) as product_count
            FROM categories 
            WHERE user_id = %s 
            ORDER BY name
        ''', (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        categories = []
        for row in rows:
            categories.append({
                "id": row[0],
                "name": row[1],
                "descripcion": row[2] or "",
                "product_count": row[3]
            })
        
        return jsonify({"data": categories}), 200
        
    except Exception as e:
        print(f"ERROR en GET clasificaciones: {str(e)}")
        return jsonify({"error": str(e)}), 500


# MEJORA 1: Endpoint para obtener UNA categoría por ID (necesario para editar)
@app.route('/usuario/<int:user_id>/clasificaciones/<int:category_id>', methods=['GET'])
def obtener_clasificacion(user_id, category_id):
    """Obtiene una categoría específica por su ID"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            'SELECT id, name, descripcion FROM categories WHERE id = %s AND user_id = %s',
            (category_id, user_id)
        )
        
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not row:
            return jsonify({"error": "Categoría no encontrada"}), 404
        
        return jsonify({
            "data": {
                "id": row[0],
                "name": row[1],
                "descripcion": row[2] or ""
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR en GET clasificacion individual: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/clasificaciones', methods=['POST'])
def crear_clasificacion(user_id):
    """Crea una nueva categoría"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        descripcion = data.get('descripcion', '').strip()
        
        if not name:
            return jsonify({"error": "El nombre es requerido"}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar si ya existe
        cursor.execute(
            'SELECT id FROM categories WHERE name = %s AND user_id = %s',
            (name, user_id)
        )
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Ya existe una categoría con ese nombre"}), 400
        
        # Insertar con descripcion (MEJORA 2)
        cursor.execute(
            'INSERT INTO categories (name, descripcion, user_id) VALUES (%s, %s, %s)',
            (name, descripcion, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Categoría creada exitosamente"}), 201
        
    except Exception as e:
        print(f"ERROR en POST clasificaciones: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/clasificaciones/<int:category_id>', methods=['PUT'])
def actualizar_clasificacion(user_id, category_id):
    """Actualiza una categoría"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        descripcion = data.get('descripcion', '').strip()
        
        if not name:
            return jsonify({"error": "El nombre es requerido"}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar que existe
        cursor.execute(
            'SELECT id FROM categories WHERE id = %s AND user_id = %s',
            (category_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Categoría no encontrada"}), 404
        
        # Actualizar
        cursor.execute(
            'UPDATE categories SET name = %s, descripcion = %s WHERE id = %s AND user_id = %s',
            (name, descripcion, category_id, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Categoría actualizada exitosamente"}), 200
        
    except Exception as e:
        print(f"ERROR en PUT clasificaciones: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/clasificaciones/<int:category_id>', methods=['DELETE'])
def eliminar_clasificacion(user_id, category_id):
    """Elimina una categoría"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar que existe
        cursor.execute(
            'SELECT id FROM categories WHERE id = %s AND user_id = %s',
            (category_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Categoría no encontrada"}), 404
        
        # Actualizar productos
        cursor.execute(
            'UPDATE products SET category_id = NULL WHERE category_id = %s AND user_id = %s',
            (category_id, user_id)
        )
        
        # Eliminar
        cursor.execute(
            'DELETE FROM categories WHERE id = %s AND user_id = %s',
            (category_id, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Categoría eliminada exitosamente"}), 200
        
    except Exception as e:
        print(f"ERROR en DELETE clasificaciones: {str(e)}")
        return jsonify({"error": str(e)}), 500

print("✅ Rutas de categorías cargadas correctamente")
