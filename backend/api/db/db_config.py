import mysql.connector
import os
from contextlib import contextmanager

def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos MySQL.
    Usa variables de entorno para la configuración.
    """
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '3306'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci'
    )
    return connection

@contextmanager
def get_db_cursor():
    """
    Context manager para manejar conexiones y cursores de base de datos.
    Uso: with get_db_cursor() as cursor:
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()

class DBError(Exception):
    """Excepción personalizada para errores de base de datos"""
    pass
