import pyodbc


SERVER = r"CCAYAL\COMPAC"
DATABASE = "Prueba_CC"
USERNAME = "sa"
PASSWORD = "compac"


def obtener_conexion():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
    )
