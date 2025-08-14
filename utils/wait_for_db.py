import time
import psycopg2
from psycopg2 import OperationalError
import os

def wait_for_postgres():
    db_user = os.environ.get("DATABASE_USERNAME", "dbuser")
    db_password = os.environ.get("DATABASE_PASSWORD", "dbpassword")
    db_name = os.environ.get("DATABASE_NAME", "dockerdjango")
    db_host = os.environ.get("DATABASE_HOST", "db")
    db_port = os.environ.get("DATABASE_PORT", 5432)

    while True:
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            conn.close()
            print("Database is ready!")
            break
        except OperationalError as e:
            print("Waiting for database...")
            time.sleep(1)

if __name__ == "__main__":
    wait_for_postgres()
