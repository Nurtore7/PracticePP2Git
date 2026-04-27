# connect.py
# Модуль для работы с подключением к базе данных
import psycopg2
from config import DB_CONFIG

def get_connection():
    """Получение соединения с базой данных"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None