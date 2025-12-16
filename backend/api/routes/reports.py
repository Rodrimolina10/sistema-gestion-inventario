from api import app
from flask import request, jsonify
from api.db.db_config import get_db_connection

# RUTAS SIMPLES DE REPORTES

@app.route('/usuario/<int:user_id>/informes/resumen-inventario', methods=['GET', 'OPTIONS'])
def informe_resumen_inventario(user_id):
    """Genera informe completo del inventario"""
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
        
        # Productos con stock bajo (1-5)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM stock s 
            JOIN products p ON s.product_id = p.id 
            WHERE p.user_id = %s AND s.quantity > 0 AND s.quantity <= 5
        ''', (user_id,))
        low_stock_count = cursor.fetchone()[0]
        
        # Productos sin stock (0)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM stock s 
            JOIN products p ON s.product_id = p.id 
            WHERE p.user_id = %s AND s.quantity = 0
        ''', (user_id,))
        out_of_stock_count = cursor.fetchone()[0]
        
        # Productos con stock bajo (detalle)
        cursor.execute('''
            SELECT p.id, p.name, s.quantity, c.name as categoria
            FROM products p
            LEFT JOIN stock s ON p.id = s.product_id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.user_id = %s AND s.quantity <= 5
            ORDER BY s.quantity ASC
        ''', (user_id,))
        
        low_stock_rows = cursor.fetchall()
        low_stock_products = []
        for row in low_stock_rows:
            low_stock_products.append({
                "id": row[0],
                "nombre": row[1],
                "cantidad": row[2],
                "categoria": row[3] or "Sin categoría"
            })
        
        # Productos por categoría
        cursor.execute('''
            SELECT COALESCE(c.name, 'Sin categoría') as categoria, COUNT(p.id) as cantidad
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.user_id = %s
            GROUP BY c.name
        ''', (user_id,))
        
        category_rows = cursor.fetchall()
        by_category = {}
        for row in category_rows:
            by_category[row[0]] = row[1]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "total_products": total_products,
            "total_units": total_units,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "low_stock_products": low_stock_products,
            "by_category": by_category
        }), 200
        
    except Exception as e:
        print(f"ERROR en GET resumen-inventario: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/informes/articulos-populares', methods=['GET', 'OPTIONS'])
def informe_articulos_populares(user_id):
    """Genera informe de artículos más pedidos"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        limit = request.args.get('limit', 10, type=int)
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT p.id, p.name, COALESCE(SUM(op.quantity), 0) as total_ordered
            FROM products p
            LEFT JOIN order_products op ON p.id = op.product_id
            WHERE p.user_id = %s
            GROUP BY p.id, p.name
            ORDER BY total_ordered DESC
            LIMIT %s
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        products = []
        for row in rows:
            products.append({
                "id": row[0],
                "name": row[1],
                "total_ordered": row[2]
            })
        
        return jsonify({"data": products}), 200
        
    except Exception as e:
        print(f"ERROR en GET articulos-populares: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/usuario/<int:user_id>/informes/pedidos-por-estado', methods=['GET', 'OPTIONS'])
def informe_pedidos_por_estado(user_id):
    """Genera informe de pedidos agrupados por estado"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT status, COUNT(*) as cantidad
            FROM purchase_orders
            WHERE user_id = %s AND status != 'deleted'
            GROUP BY status
        ''', (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        by_status = {}
        for row in rows:
            by_status[row[0]] = row[1]
        
        return jsonify({"data": by_status}), 200
        
    except Exception as e:
        print(f"ERROR en GET pedidos-por-estado: {str(e)}")
        return jsonify({"error": str(e)}), 500

print("✅ Rutas de reportes cargadas correctamente")