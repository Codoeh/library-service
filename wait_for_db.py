import time
import psycopg2
from django.db import OperationalError
import os

db_host = os.environ.get("DATABASE_HOST", "db")
db_name = os.environ.get("DATABASE_NAME", "postgres")
db_user = os.environ.get("DATABASE_USERNAME", "postgres")
db_password = os.environ.get("DATABASE_PASSWORD", "")

print("Waiting for database...")

while True:
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host
        )
        conn.close()
        print("Database is ready!")
        break
    except OperationalError:
        print("Database unavailable, waiting 1 second...")
        time.sleep(1)
