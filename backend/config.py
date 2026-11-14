"""Configuración centralizada. Lee variables de entorno con defaults seguros para Laragon."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # MySQL (Laragon por defecto: localhost, root, sin password)
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "portfolio_dev")

    # JWT
    JWT_SECRET = os.environ.get("JWT_SECRET", "cambia-esta-clave-super-secreta")
    JWT_ALGORITHM = "HS256"
    JWT_EXP_HOURS = int(os.environ.get("JWT_EXP_HOURS", "24"))

    # Flask
    FLASK_PORT = int(os.environ.get("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    @classmethod
    def db_config(cls):
        return {
            "host": cls.MYSQL_HOST,
            "port": cls.MYSQL_PORT,
            "user": cls.MYSQL_USER,
            "password": cls.MYSQL_PASSWORD,
            "database": cls.MYSQL_DATABASE,
        }