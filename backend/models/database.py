"""Wrapper OOP sobre mysql-connector-python. Provee contexto para obtener conexión y cursor."""
import mysql.connector
from mysql.connector import pooling
from config import Config


class Database:
    """Singleton de pool de conexiones MySQL."""
    _pool = None

    @classmethod
    def _init_pool(cls):
        if cls._pool is None:
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="portfolio_pool",
                pool_size=5,
                autocommit=False,
                **Config.db_config(),
            )

    @classmethod
    def get_connection(cls):
        cls._init_pool()
        return cls._pool.get_connection()


class Cursor:
    """Context manager para obtener (conn, cursor) y manejar commit/rollback/close."""

    def __init__(self, dictionary=True, commit=False):
        self.dictionary = dictionary
        self.commit = commit
        self.conn = None
        self.cur = None

    def __enter__(self):
        self.conn = Database.get_connection()
        self.cur = self.conn.cursor(dictionary=self.dictionary)
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None and self.commit:
                self.conn.commit()
            elif exc_type is not None:
                self.conn.rollback()
        finally:
            if self.cur is not None:
                self.cur.close()
            if self.conn is not None:
                self.conn.close()