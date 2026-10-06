
import os

SERVER = os.getenv("DB_SERVER", r"CCAYAL\COMPAC")
DATABASE = os.getenv("DB_DATABASE", "Prueba_CC")
USERNAME = os.getenv("DB_USERNAME", "sa")
PASSWORD = os.getenv("DB_PASSWORD", "compac")
DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")