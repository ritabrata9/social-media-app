import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from project root
load_dotenv(dotenv_path=Path('.') / '.env')


try:
    conn = psycopg2.connect(
        host=os.getenv("DATABASE_HOSTNAME"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USERNAME"),
        password=os.getenv("DATABASE_PASSWORD"),
        port=os.getenv("DATABASE_PORT"),
        cursor_factory=RealDictCursor
    )
    cursor = conn.cursor()
    print("Database connection successful")

except Exception as error:
    print("Database connection failed")
    print("ERROR:", error)
    raise error