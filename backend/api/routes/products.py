from api import app
from flask import request, jsonify
from api.db.db_config import get_db_connection

# RUTAS SIMPLES DE PRODUCTOS

@app.route('/usuario/<int:user_id>/articulos', methods=['GET', 'OPTIONS'])
def obtener_articulos(user_id):
    """Obtiene todos los productos de un usuario"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT p.id, p.name, p.price, p.category_id,
                   c.name as category_name,
                   COALESCE(s.quantity, 0) as stock_quantity
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN stock s ON p.id = s.product_id
            WHERE p.user_id = %s
            ORDER BY p.name
        ''', (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        products = []
        for row in rows:
            products.append({
                "id": row[0],
                "name": row[1],
                "price": float(row[2]) if row[2] else 0,
                "category_id": row[3],
                "category_name": row[4] or "Sin categoría",
                "stock": row[5]
            })
        
        return jsonify({"data": products}), 200
        
    except Exception as e:
        print(f"ERROR en GET articulos: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/articulos', methods=['POST'])
def crear_articulo(user_id):
    """Crea un nuevo producto"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        price = float(data.get('price', 0))
        category_id = data.get('category_id')
        quantity = int(data.get('quantity', 0))
        
        if not name:
            return jsonify({"error": "El nombre es requerido"}), 400
        
        if price < 0:
            return jsonify({"error": "El precio no puede ser negativo"}), 400
            
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar si ya existe
        cursor.execute(
            'SELECT id FROM products WHERE name = %s AND user_id = %s',
            (name, user_id)
        )
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Ya existe un producto con ese nombre"}), 400
        
        # Insertar producto (el trigger creará el stock automáticamente)
        cursor.execute(
            'INSERT INTO products (name, price, category_id, user_id) VALUES (%s, %s, %s, %s)',
            (name, price, category_id, user_id)
        )
        product_id = cursor.lastrowid
        
        # Si se especificó cantidad inicial, actualizar el stock
        if quantity > 0:
            cursor.execute(
                'UPDATE stock SET quantity = %s WHERE product_id = %s',
                (quantity, product_id)
            )
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Producto creado exitosamente"}), 201
        
    except Exception as e:
        print(f"ERROR en POST articulos: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/articulos/<int:product_id>', methods=['PUT'])
def actualizar_articulo(user_id, product_id):
    """Actualiza un producto"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        price = float(data.get('price', 0))
        category_id = data.get('category_id')
        
        if not name:
            return jsonify({"error": "El nombre es requerido"}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar que existe
        cursor.execute(
            'SELECT id FROM products WHERE id = %s AND user_id = %s',
            (product_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Producto no encontrado"}), 404
        
        # Actualizar
        cursor.execute(
            'UPDATE products SET name = %s, price = %s, category_id = %s WHERE id = %s AND user_id = %s',
            (name, price, category_id, product_id, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Producto actualizado exitosamente"}), 200
        
    except Exception as e:
        print(f"ERROR en PUT articulos: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/articulos/<int:product_id>', methods=['DELETE'])
def eliminar_articulo(user_id, product_id):
    """Elimina un producto"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar que existe
        cursor.execute(
            'SELECT id FROM products WHERE id = %s AND user_id = %s',
            (product_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Producto no encontrado"}), 404
        
        # Eliminar stock
        cursor.execute(
            'DELETE FROM stock WHERE product_id = %s',
            (product_id,)
        )
        
        # Eliminar producto
        cursor.execute(
            'DELETE FROM products WHERE id = %s AND user_id = %s',
            (product_id, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Producto eliminado exitosamente"}), 200
        
    except Exception as e:
        print(f"ERROR en DELETE articulos: {str(e)}")
        return jsonify({"error": str(e)}), 500

print("✅ Rutas de productos cargadas correctamente")