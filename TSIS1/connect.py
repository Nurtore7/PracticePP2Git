import psycopg2
import os
from config import config

def get_connection():
    """Установка соединения с БД"""
    try:
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

def init_database():
    """Инициализация базы данных (создание таблиц)"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            # Получаем путь к текущей директории
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Читаем и выполняем schema.sql
            schema_path = os.path.join(current_dir, 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                    cur.execute(schema_sql)
                print("schema.sql выполнен успешно")
            else:
                print(f"Файл не найден: {schema_path}")
                return False
            
            # Читаем и выполняем procedures.sql
            procedures_path = os.path.join(current_dir, 'procedures.sql')
            if os.path.exists(procedures_path):
                with open(procedures_path, 'r', encoding='utf-8') as f:
                    procedures_sql = f.read()
                    cur.execute(procedures_sql)
                print("procedures.sql выполнен успешно")
            else:
                print(f"Файл не найден: {procedures_path}")
                return False
            
            conn.commit()
            print("База данных успешно инициализирована")
            return True
            
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()