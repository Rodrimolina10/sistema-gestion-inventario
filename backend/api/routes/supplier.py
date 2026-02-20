from api import app
from flask import request, jsonify
from api.db.db_config import get_db_connection

# RUTAS DE PROVEEDORES

@app.route('/usuario/<int:user_id>/distribuidores', methods=['GET', 'OPTIONS'])
def obtener_distribuidores(user_id):
    """Obtiene todos los proveedores"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT s.id, s.name_supplier, s.phone, s.mail,
                   COUNT(sp.product_id) as product_count
            FROM suppliers s
            LEFT JOIN suppliers_products sp ON s.id = sp.supplier_id
            WHERE s.user_id = %s
            GROUP BY s.id
            ORDER BY s.name_supplier
        ''', (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        suppliers = []
        for row in rows:
            suppliers.append({
                "id": row[0],
                "name": row[1],
                "contact": "",
                "phone": row[2] or "",
                "email": row[3] or "",
                "product_count": row[4]
            })
        
        return jsonify({"data": suppliers}), 200
        
    except Exception as e:
        print(f"ERROR en GET distribuidores: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/distribuidores', methods=['POST'])
def crear_distribuidor(user_id):
    """Crea un nuevo proveedor"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        
        if not name:
            return jsonify({"error": "El nombre es requerido"}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            'SELECT id FROM suppliers WHERE name_supplier = %s AND user_id = %s',
            (name, user_id)
        )
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Ya existe un proveedor con ese nombre"}), 400
        
        cursor.execute(
            'INSERT INTO suppliers (name_supplier, phone, mail, user_id) VALUES (%s, %s, %s, %s)',
            (name, phone, email, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Proveedor creado exitosamente"}), 201
        
    except Exception as e:
        print(f"ERROR en POST distribuidores: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/distribuidores/<int:supplier_id>', methods=['DELETE', 'OPTIONS'])
def eliminar_distribuidor(user_id, supplier_id):
    """Elimina un proveedor"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            'SELECT id FROM suppliers WHERE id = %s AND user_id = %s',
            (supplier_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Proveedor no encontrado"}), 404
        
        cursor.execute(
            'DELETE FROM suppliers_products WHERE supplier_id = %s',
            (supplier_id,)
        )
        
        cursor.execute(
            'DELETE FROM suppliers WHERE id = %s AND user_id = %s',
            (supplier_id, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Proveedor eliminado exitosamente"}), 200
        
    except Exception as e:
        print(f"ERROR en DELETE distribuidores: {str(e)}")
        return jsonify({"error": str(e)}), 500


# MEJORA 3: VINCULAR PROVEEDOR CON PRODUCTO

@app.route('/usuario/<int:user_id>/proveedores/<int:supplier_id>/productos/<int:product_id>', methods=['POST', 'OPTIONS'])
def vincular_proveedor_producto(user_id, supplier_id, product_id):
    """Vincula un proveedor con un producto"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            'SELECT id FROM suppliers WHERE id = %s AND user_id = %s',
            (supplier_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Proveedor no encontrado"}), 404
        
        cursor.execute(
            'SELECT id FROM products WHERE id = %s AND user_id = %s',
            (product_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Producto no encontrado"}), 404
        
        cursor.execute(
            'SELECT 1 FROM suppliers_products WHERE supplier_id = %s AND product_id = %s',
            (supplier_id, product_id)
        )
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Esta relación ya existe"}), 400
        
        cursor.execute(
            'INSERT INTO suppliers_products (supplier_id, product_id, user_id) VALUES (%s, %s, %s)',
            (supplier_id, product_id, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Proveedor vinculado al producto exitosamente"}), 201
        
    except Exception as e:
        print(f"ERROR en vincular: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/proveedores/<int:supplier_id>/productos/<int:product_id>', methods=['DELETE'])
def desvincular_proveedor_producto(user_id, supplier_id, product_id):
    """Elimina la relación entre proveedor y producto"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            'DELETE FROM suppliers_products WHERE supplier_id = %s AND product_id = %s AND user_id = %s',
            (supplier_id, product_id, user_id)
        )
        
        if cursor.rowcount == 0:
            cursor.close()
            connection.close()
            return jsonify({"error": "Relación no encontrada"}), 404
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Relación eliminada exitosamente"}), 200
        
    except Exception as e:
        print(f"ERROR en desvincular: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/distribuidores/<int:supplier_id>/productos', methods=['GET', 'OPTIONS'])
def obtener_productos_proveedor(user_id, supplier_id):
    """Obtiene todos los productos de un proveedor"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT p.id, p.name, p.price
            FROM products p
            INNER JOIN suppliers_products sp ON p.id = sp.product_id
            WHERE sp.supplier_id = %s AND sp.user_id = %s
        ''', (supplier_id, user_id))
        
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        products = []
        for row in rows:
            products.append({
                "id": row[0],
                "name": row[1],
                "price": float(row[2])
            })
        
        return jsonify({"data": products}), 200
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/articulos/<int:product_id>/proveedores', methods=['GET', 'OPTIONS'])
def obtener_proveedores_producto(user_id, product_id):
    """Obtiene todos los proveedores de un producto"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT s.id, s.name_supplier, s.phone, s.mail
            FROM suppliers s
            INNER JOIN suppliers_products sp ON s.id = sp.supplier_id
            WHERE sp.product_id = %s AND sp.user_id = %s
        ''', (product_id, user_id))
        
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        suppliers = []
        for row in rows:
            suppliers.append({
                "id": row[0],
                "name": row[1],
                "phone": row[2] or "",
                "email": row[3] or ""
            })
        
        return jsonify({"data": suppliers}), 200
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500


print("✅ Rutas de proveedores cargadas correctamente")