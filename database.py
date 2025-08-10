import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

# Remove Supabase-specific parameters that psycopg2 doesn't understand
if DATABASE_URL:
    parsed_url = urlparse(DATABASE_URL)
    if 'supa' in parse_qs(parsed_url.query):
        query_params = parse_qs(parsed_url.query)
        del query_params['supa']
        # Rebuild the URL without the 'supa' parameter
        new_query = urlencode(query_params, doseq=True)
        DATABASE_URL = urlunparse(parsed_url._replace(query=new_query))

# Normalize common DSN forms
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # SQLAlchemy expects 'postgresql+psycopg2://' for psycopg2 driver
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

if not DATABASE_URL:
    # Fallback to SQLite (local file)
    sqlite_path = os.path.join(os.path.dirname(__file__), "..", "healthcare.db")
    sqlite_path = os.path.abspath(sqlite_path)
    DATABASE_URL = f"sqlite:///{sqlite_path}"

# For SQLite, need check_same_thread=False when used with FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
from typing import Generator

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
