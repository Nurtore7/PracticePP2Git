import psycopg2
from config import DB_CONFIG

def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        print("Successfully connected")
        return conn

    except Exception as e:
        print("Error:", e)
        return None


# чтобы можно было проверить отдельно
if __name__ == "__main__":
    get_connection()