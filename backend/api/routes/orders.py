from api import app
from flask import request, jsonify
from api.db.db_config import get_db_connection
from datetime import date

# RUTAS SIMPLES DE ÓRDENES

@app.route('/usuario/<int:user_id>/pedidos', methods=['GET', 'OPTIONS'])
def obtener_pedidos(user_id):
    """Obtiene todas las órdenes"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT po.id, po.order_date, po.received_date, po.status,
                   COUNT(op.product_id) as product_count
            FROM purchase_orders po
            LEFT JOIN order_products op ON po.id = op.order_id
            WHERE po.user_id = %s AND po.status != 'deleted'
            GROUP BY po.id
            ORDER BY po.order_date DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        orders = []
        for row in rows:
            orders.append({
                "id": row[0],
                "order_date": str(row[1]),
                "received_date": str(row[2]) if row[2] else None,
                "status": row[3],
                "product_count": row[4]
            })
        
        return jsonify({"data": orders}), 200
        
    except Exception as e:
        print(f"ERROR en GET pedidos: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/pedidos', methods=['POST'])
def crear_pedido(user_id):
    """Crea una nueva orden"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({"error": "Debe incluir al menos un producto"}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Crear orden
        cursor.execute(
            'INSERT INTO purchase_orders (order_date, status, user_id) VALUES (%s, %s, %s)',
            (date.today(), 'pending', user_id)
        )
        order_id = cursor.lastrowid
        
        # Agregar productos a la orden
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            
            if product_id and quantity > 0:
                cursor.execute(
                    'INSERT INTO order_products (order_id, product_id, quantity) VALUES (%s, %s, %s)',
                    (order_id, product_id, quantity)
                )
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Orden creada exitosamente", "order_id": order_id}), 201
        
    except Exception as e:
        print(f"ERROR en POST pedidos: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/pedidos/<int:order_id>', methods=['GET', 'OPTIONS'])
def obtener_pedido_detalle(user_id, order_id):
    """Obtiene los detalles de una orden"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Obtener orden
        cursor.execute('''
            SELECT id, order_date, received_date, status
            FROM purchase_orders
            WHERE id = %s AND user_id = %s
        ''', (order_id, user_id))
        
        order_row = cursor.fetchone()
        if not order_row:
            cursor.close()
            connection.close()
            return jsonify({"error": "Orden no encontrada"}), 404
        
        # Obtener productos de la orden
        cursor.execute('''
            SELECT p.id, p.name, op.quantity
            FROM order_products op
            JOIN products p ON op.product_id = p.id
            WHERE op.order_id = %s
        ''', (order_id,))
        
        product_rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        products = []
        for row in product_rows:
            products.append({
                "product_id": row[0],
                "product_name": row[1],
                "quantity": row[2]
            })
        
        return jsonify({
            "id": order_row[0],
            "order_date": str(order_row[1]),
            "received_date": str(order_row[2]) if order_row[2] else None,
            "status": order_row[3],
            "products": products
        }), 200
        
    except Exception as e:
        print(f"ERROR en GET pedido detalle: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/pedidos/<int:order_id>/confirmar', methods=['PUT', 'OPTIONS'])
def confirmar_pedido(user_id, order_id):
    """Confirma una orden y actualiza el stock"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar que la orden existe
        cursor.execute(
            'SELECT id, status FROM purchase_orders WHERE id = %s AND user_id = %s',
            (order_id, user_id)
        )
        order = cursor.fetchone()
        if not order:
            cursor.close()
            connection.close()
            return jsonify({"error": "Orden no encontrada"}), 404
        
        if order[1] == 'completed':
            cursor.close()
            connection.close()
            return jsonify({"error": "La orden ya fue confirmada"}), 400
        
        # Obtener productos de la orden
        cursor.execute('''
            SELECT product_id, quantity 
            FROM order_products 
            WHERE order_id = %s
        ''', (order_id,))
        
        products = cursor.fetchall()
        
        # Actualizar stock de cada producto
        for product_id, quantity in products:
            cursor.execute('''
                UPDATE stock 
                SET quantity = quantity + %s 
                WHERE product_id = %s
            ''', (quantity, product_id))
        
        # Actualizar estado de la orden
        cursor.execute('''
            UPDATE purchase_orders 
            SET status = 'completed', received_date = %s 
            WHERE id = %s
        ''', (date.today(), order_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Orden confirmada y stock actualizado"}), 200
        
    except Exception as e:
        print(f"ERROR en PUT confirmar pedido: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/pedidos/<int:order_id>', methods=['DELETE'])
def eliminar_pedido(user_id, order_id):
    """Elimina (marca como eliminada) una orden"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar que existe
        cursor.execute(
            'SELECT id FROM purchase_orders WHERE id = %s AND user_id = %s',
            (order_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "Orden no encontrada"}), 404
        
        # Marcar como eliminada
        cursor.execute(
            "UPDATE purchase_orders SET status = 'deleted' WHERE id = %s",
            (order_id,)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Orden eliminada exitosamente"}), 200
        
    except Exception as e:
        print(f"ERROR en DELETE pedidos: {str(e)}")
        return jsonify({"error": str(e)}), 500

print("✅ Rutas de órdenes cargadas correctamente")