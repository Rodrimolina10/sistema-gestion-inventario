from api.db.db_config import get_db_connection, DBError

class Report:
    """Modelo para generación de reportes del sistema"""

    @staticmethod
    def purchases_summary_by_period(user_id, start_date, end_date):
        """
        Genera resumen de compras por período.
        
        Args:
            user_id (int): ID del usuario
            start_date (str): Fecha de inicio (YYYY-MM-DD)
            end_date (str): Fecha de fin (YYYY-MM-DD)
            
        Returns:
            list: Resumen de compras
            
        Raises:
            DBError: Si no hay compras en el período
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT 
                        po.order_date,
                        po.id as order_id,
                        po.status,
                        COUNT(op.product_id) as total_products,
                        SUM(op.quantity) as total_items,
                        SUM(op.quantity * p.price) as total_amount
                    FROM purchase_orders po
                    JOIN order_products op ON po.id = op.order_id
                    JOIN products p ON op.product_id = p.id
                    WHERE po.user_id = %s 
                        AND po.order_date BETWEEN %s AND %s
                        AND po.status != 'deleted'
                    GROUP BY po.id, po.order_date, po.status
                    ORDER BY po.order_date DESC
                    ''',
                    (user_id, start_date, end_date)
                )
                data = cursor.fetchall()

        if not data:
            raise DBError("No se encontraron compras en el período especificado")

        return [
            {
                "order_date": str(row[0]),
                "order_id": row[1],
                "status": row[2],
                "total_products": row[3],
                "total_items": row[4],
                "total_amount": float(row[5])
            }
            for row in data
        ]

    @staticmethod
    def top_products(user_id, limit=5):
        """
        Obtiene los productos más comprados.
        
        Args:
            user_id (int): ID del usuario
            limit (int): Número máximo de productos a retornar
            
        Returns:
            list: Productos más comprados
            
        Raises:
            DBError: Si no hay productos comprados
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT 
                        p.id as product_id,
                        p.name AS product_name,
                        SUM(op.quantity) AS total_quantity,
                        COUNT(DISTINCT po.id) as times_ordered,
                        p.price,
                        SUM(op.quantity * p.price) as total_spent
                    FROM order_products op
                    JOIN products p ON op.product_id = p.id
                    JOIN purchase_orders po ON op.order_id = po.id
                    WHERE po.user_id = %s AND po.status = 'completed'
                    GROUP BY p.id, p.name, p.price
                    ORDER BY total_quantity DESC
                    LIMIT %s
                    ''',
                    (user_id, limit)
                )
                data = cursor.fetchall()

        if not data:
            raise DBError("No se encontraron productos comprados")

        return [
            {
                "product_id": row[0],
                "product_name": row[1],
                "total_quantity": row[2],
                "times_ordered": row[3],
                "unit_price": float(row[4]),
                "total_spent": float(row[5])
            }
            for row in data
        ]

    @staticmethod
    def stock_summary(user_id):
        """
        Genera resumen del estado del stock.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            dict: Resumen del stock
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Total de productos
                cursor.execute(
                    'SELECT COUNT(*) FROM stock WHERE user_id = %s',
                    (user_id,)
                )
                total_products = cursor.fetchone()[0]

                # Total de unidades
                cursor.execute(
                    'SELECT SUM(quantity) FROM stock WHERE user_id = %s',
                    (user_id,)
                )
                total_units = cursor.fetchone()[0] or 0

                # Valor total del inventario
                cursor.execute(
                    '''SELECT SUM(s.quantity * p.price) 
                       FROM stock s
                       JOIN products p ON s.product_id = p.id
                       WHERE s.user_id = %s''',
                    (user_id,)
                )
                total_value = cursor.fetchone()[0] or 0

                # Productos con stock bajo (<=5)
                cursor.execute(
                    'SELECT COUNT(*) FROM stock WHERE user_id = %s AND quantity <= 5',
                    (user_id,)
                )
                low_stock_count = cursor.fetchone()[0]

                # Productos sin stock
                cursor.execute(
                    'SELECT COUNT(*) FROM stock WHERE user_id = %s AND quantity = 0',
                    (user_id,)
                )
                out_of_stock = cursor.fetchone()[0]

                # Productos por categoría
                cursor.execute(
                    '''SELECT 
                           COALESCE(c.name, 'Sin categoría') as category_name,
                           COUNT(p.id) as product_count,
                           SUM(s.quantity) as total_units
                       FROM products p
                       LEFT JOIN categories c ON p.category_id = c.id
                       JOIN stock s ON p.id = s.product_id
                       WHERE p.user_id = %s
                       GROUP BY c.name
                       ORDER BY product_count DESC''',
                    (user_id,)
                )
                by_category = cursor.fetchall()

        return {
            "total_products": total_products,
            "total_units": int(total_units),
            "total_value": float(total_value),
            "low_stock_count": low_stock_count,
            "out_of_stock": out_of_stock,
            "by_category": [
                {
                    "category": row[0],
                    "products": row[1],
                    "units": row[2]
                }
                for row in by_category
            ]
        }

    @staticmethod
    def orders_by_status(user_id):
        """
        Obtiene resumen de órdenes por estado.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            dict: Resumen de órdenes por estado
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''SELECT 
                           status,
                           COUNT(*) as count,
                           SUM((SELECT SUM(op.quantity * p.price)
                                FROM order_products op
                                JOIN products p ON op.product_id = p.id
                                WHERE op.order_id = po.id)) as total_amount
                       FROM purchase_orders po
                       WHERE user_id = %s
                       GROUP BY status''',
                    (user_id,)
                )
                data = cursor.fetchall()

        return [
            {
                "status": row[0],
                "count": row[1],
                "total_amount": float(row[2]) if row[2] else 0
            }
            for row in data
        ]

    @staticmethod
    def recent_activity(user_id, days=30):
        """
        Obtiene actividad reciente del usuario.
        
        Args:
            user_id (int): ID del usuario
            days (int): Número de días hacia atrás
            
        Returns:
            dict: Resumen de actividad reciente
        """
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Órdenes recientes
                cursor.execute(
                    '''SELECT COUNT(*) 
                       FROM purchase_orders 
                       WHERE user_id = %s 
                       AND order_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)''',
                    (user_id, days)
                )
                recent_orders = cursor.fetchone()[0]

                # Productos agregados recientemente
                cursor.execute(
                    '''SELECT COUNT(*) 
                       FROM products 
                       WHERE user_id = %s 
                       AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)''',
                    (user_id, days)
                )
                recent_products = cursor.fetchone()[0]

                # Órdenes completadas recientemente
                cursor.execute(
                    '''SELECT COUNT(*) 
                       FROM purchase_orders 
                       WHERE user_id = %s 
                       AND status = 'completed'
                       AND received_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)''',
                    (user_id, days)
                )
                completed_orders = cursor.fetchone()[0]

        return {
            "period_days": days,
            "recent_orders": recent_orders,
            "recent_products": recent_products,
            "completed_orders": completed_orders
        }
