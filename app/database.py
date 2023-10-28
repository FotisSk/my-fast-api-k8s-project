import psycopg2 
import os
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

HOST = "172.27.249.28"
DATABASE = os.environ.get("DATABASE")
DB_USER = os.environ.get("DB_USER")
PASSWORD = os.environ.get("PASSWORD")

# format --> SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<ip-address or hostname>/<database_name>"
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{PASSWORD}@{HOST}/{DATABASE}"

# engine is responsible for SQLAlchemy to establish a connection to the postgreSQL database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# create a session to be able to talk to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# all of the models that we will create will be extending this Base class
Base = declarative_base()

# get a session with the database for every request, after the request is done we close it out
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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