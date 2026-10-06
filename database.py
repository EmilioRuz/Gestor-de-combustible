"""
Modulo de conexion a la base de datos con context manager.
"""
import pyodbc
from contextlib import contextmanager

from config import SERVER, DATABASE, USERNAME, PASSWORD, DRIVER


def obtener_conexion():
    return pyodbc.connect(
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
    )


@contextmanager
def conexion_db():
    """
    Context manager que abre una conexion, entrega (conn, cursor),
    hace commit si todo sale bien o rollback si hay error,
    y siempre cierra cursor y conexion.
    """
    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        yield conn, cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()