from api import app
from flask import request, jsonify
from api.db.db_config import get_db_connection

# RUTAS SIMPLES DE PROVEEDORES

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
                "contact": "",  # No existe en la tabla
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
        
        # Verificar si ya existe
        cursor.execute(
            'SELECT id FROM suppliers WHERE name_supplier = %s AND user_id = %s',
            (name, user_id)
        )
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Ya existe un proveedor con ese nombre"}), 400
        
        # Insertar (contact no existe en la tabla)
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


@app.route('/usuario/<int:user_id>/distribuidores/<int:supplier_id>', methods=['DELETE'])
def eliminar_distribuidor(user_id, supplier_id):
    """Elimina un proveedor"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar que existe
        cursor.execute(
            'SELECT id FROM suppliers WHERE id = %s AND user_id = %s',
            (supplier_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Proveedor no encontrado"}), 404
        
        # Eliminar relaciones con productos
        cursor.execute(
            'DELETE FROM suppliers_products WHERE supplier_id = %s',
            (supplier_id,)
        )
        
        # Eliminar proveedor
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

print("✅ Rutas de proveedores cargadas correctamente")