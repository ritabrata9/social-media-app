from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path

# load credentials from .env file
load_dotenv(dotenv_path=Path('.') / '.env')

# build the connection URL from env vars
# format: postgresql://user:password@host:port/dbname
DATABASE_URL = (
    f"postgresql://{os.getenv('DATABASE_USERNAME')}:{os.getenv('DATABASE_PASSWORD')}"
    f"@{os.getenv('DATABASE_HOSTNAME')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# engine is the core connection to the database — equivalent to psycopg2.connect()
# it manages the connection pool under the hood
engine = create_engine(DATABASE_URL)

# sessionmaker creates a factory for database sessions
# each request gets its own session — used to run queries and commit transactions
# autocommit=False means we manually call commit(); autoflush=False gives us control over when flushes happen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class all ORM models inherit from
# SQLAlchemy uses it to track all model classes and map them to tables
Base = declarative_base()


# dependency function used by FastAPI to provide a db session per request
# yields a session, then closes it automatically when the request is done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
