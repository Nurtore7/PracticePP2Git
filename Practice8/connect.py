import psycopg2
from config import host, database, user, password

def connect():
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        print("Connected successfully")
        return conn
    except Exception as e:
        print("Error:", e)
        return None

if __name__ == "__main__":
    connect()