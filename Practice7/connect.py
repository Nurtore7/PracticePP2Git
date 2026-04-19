import psycopg2
from config import DB_CONFIG

def connect():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Connected successfully")
        return conn
    except:
        print("Error connecting to database")
if __name__ == "__main__":
    connect()