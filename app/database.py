import psycopg2 
import os
from psycopg2.extras import RealDictCursor

HOST = "172.27.75.122"
DATABASE = os.environ.get("DATABASE")
DB_USER = os.environ.get("DB_USER")
PASSWORD = os.environ.get("PASSWORD")

class DatabaseHandler:

    def __init__(self) -> None:
        try:
            self.conn = psycopg2.connect(
                host=HOST,
                database=DATABASE,
                user=DB_USER,
                password=PASSWORD,
                cursor_factory=RealDictCursor
            )
        except Exception as e:
            print(f"Connecting to database failed: {e}")

    def get_connection(self):
        return self.conn