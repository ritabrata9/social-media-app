import psycopg2

# RealDictCursor makes psycopg2 return rows as dicts {"id": 1, "title": "Hello"}
# instead of plain tuples (1, "Hello") — easier to work with and required for FastAPI JSON responses
from psycopg2.extras import RealDictCursor

import os
from dotenv import load_dotenv
from pathlib import Path

# reads the .env file and injects its values into the process environment
# so os.getenv() can access them — keeps credentials out of source code and off GitHub
load_dotenv(dotenv_path=Path('.') / '.env')

try:
    # conn is the actual TCP connection to the PostgreSQL server — think of it as the session
    # it tracks all uncommitted changes; calling conn.commit() flushes them to disk permanently
    # credentials are pulled from .env at runtime via os.getenv()
    conn = psycopg2.connect(
        host=os.getenv("DATABASE_HOSTNAME"),       # e.g. localhost
        database=os.getenv("DATABASE_NAME"),       # the target database
        user=os.getenv("DATABASE_USERNAME"),       # postgres user
        password=os.getenv("DATABASE_PASSWORD"),   # postgres password
        port=os.getenv("DATABASE_PORT"),           # default postgres port is 5432
        cursor_factory=RealDictCursor              # every cursor from this conn returns dicts
    )

    # cursor is the tool used to send SQL to the server via the connection above
    # cursor.execute() runs a query, cursor.fetchone()/fetchall() retrieves results
    # one conn can have multiple cursors, but one is enough here
    cursor = conn.cursor()
    print("Database connection successful")

except Exception as error:
    print("Database connection failed")
    print("ERROR:", error)
    # re-raise so the app crashes immediately on startup with a clear message
    # without this, conn and cursor are never assigned — every request would then fail
    # with a confusing AttributeError instead of an obvious db error
    raise error