import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    """Конфигурация подключения к базе данных"""

    @staticmethod
    def get_connection():
        """Получение подключения к PostgreSQL"""
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'instagram_data'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432')
        )

    @staticmethod
    def get_dict_connection():
        """Получение подключения с возвратом результатов как словарей"""
        conn = DatabaseConfig.get_connection()
        conn.cursor_factory = RealDictCursor
        return conn
