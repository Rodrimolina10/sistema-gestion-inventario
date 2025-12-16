from api import app
from flask import request, jsonify
from api.db.db_config import get_db_connection

# RUTAS SIMPLES DE INVENTARIO/STOCK

@app.route('/usuario/<int:user_id>/inventario', methods=['GET', 'OPTIONS'])
def obtener_inventario(user_id):
    """Obtiene el inventario completo"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT p.id, p.name, p.price, c.name as category_name, 
                   s.quantity, p.category_id
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN stock s ON p.id = s.product_id
            WHERE p.user_id = %s
            ORDER BY p.name
        ''', (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        items = []
        for row in rows:
            items.append({
                "id": row[0],
                "name": row[1],
                "price": float(row[2]) if row[2] else 0,
                "category_name": row[3] or "Sin categoría",
                "quantity": row[4] or 0,
                "category_id": row[5]
            })
        
        return jsonify({"data": items}), 200
        
    except Exception as e:
        print(f"ERROR en GET inventario: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/inventario/<int:product_id>', methods=['PUT', 'OPTIONS'])
def actualizar_stock(user_id, product_id):
    """Actualiza el stock de un producto"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        quantity = int(data.get('quantity', 0))
        
        if quantity < 0:
            return jsonify({"error": "La cantidad no puede ser negativa"}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar que el producto existe
        cursor.execute(
            'SELECT id FROM products WHERE id = %s AND user_id = %s',
            (product_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Producto no encontrado"}), 404
        
        # Actualizar stock
        cursor.execute(
            'UPDATE stock SET quantity = %s WHERE product_id = %s',
            (quantity, product_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Stock actualizado exitosamente"}), 200
        
    except Exception as e:
        print(f"ERROR en PUT inventario: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/inventario/alerta-bajo', methods=['GET', 'OPTIONS'])
def obtener_stock_bajo(user_id):
    """Obtiene productos con stock bajo (<=5)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT p.id, p.name, s.quantity, c.name as category_name
            FROM products p
            LEFT JOIN stock s ON p.id = s.product_id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.user_id = %s AND s.quantity <= 5
            ORDER BY s.quantity ASC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        items = []
        for row in rows:
            items.append({
                "id": row[0],
                "name": row[1],
                "quantity": row[2],
                "category_name": row[3] or "Sin categoría"
            })
        
        return jsonify({"data": items}), 200
        
    except Exception as e:
        print(f"ERROR en GET alerta-bajo: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/inventario/estadisticas', methods=['GET', 'OPTIONS'])
def obtener_estadisticas_inventario(user_id):
    """Obtiene estadísticas del inventario"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Total productos
        cursor.execute('SELECT COUNT(*) FROM products WHERE user_id = %s', (user_id,))
        total_products = cursor.fetchone()[0]
        
        # Total unidades
        cursor.execute('''
            SELECT COALESCE(SUM(s.quantity), 0) 
            FROM stock s 
            JOIN products p ON s.product_id = p.id 
            WHERE p.user_id = %s
        ''', (user_id,))
        total_units = cursor.fetchone()[0]
        
        # Productos con stock bajo
        cursor.execute('''
            SELECT COUNT(*) 
            FROM stock s 
            JOIN products p ON s.product_id = p.id 
            WHERE p.user_id = %s AND s.quantity <= 5 AND s.quantity > 0
        ''', (user_id,))
        low_stock = cursor.fetchone()[0]
        
        # Productos sin stock
        cursor.execute('''
            SELECT COUNT(*) 
            FROM stock s 
            JOIN products p ON s.product_id = p.id 
            WHERE p.user_id = %s AND s.quantity = 0
        ''', (user_id,))
        out_of_stock = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "total_products": total_products,
            "total_units": total_units,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock
        }), 200
        
    except Exception as e:
        print(f"ERROR en GET estadisticas: {str(e)}")
        return jsonify({"error": str(e)}), 500

print("✅ Rutas de inventario/stock cargadas correctamente")
