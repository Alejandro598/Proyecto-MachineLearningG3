import mysql.connector
from fastapi import HTTPException
from config.app_config import DB_CONFIG 

def get_db():
    """
    Dependencia para obtener una conexión a la base de datos y un cursor.
    Asegura que la conexión se cierre después de la solicitud.
    """
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        yield conn, cursor
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()