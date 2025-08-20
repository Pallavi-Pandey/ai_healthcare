import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

# If no database URL is provided, use SQLite as default
if not DATABASE_URL:
    # Fallback to SQLite (local file)
    sqlite_path = os.path.join(os.path.dirname(__file__), "..", "healthcare.db")
    sqlite_path = os.path.abspath(sqlite_path)
    DATABASE_URL = f"sqlite+aiosqlite:///{sqlite_path}"
    print(f"Using SQLite database at: {sqlite_path}")
else:
    # For PostgreSQL URLs
    if DATABASE_URL.startswith("postgres://"):
        # Convert postgres:// to postgresql+asyncpg://
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    
    # Remove any problematic query parameters
    parsed_url = urlparse(DATABASE_URL)
    if parsed_url.query:
        query_params = parse_qs(parsed_url.query)
        # Remove any problematic parameters
        for param in ['supa', 'sslmode']:
            if param in query_params:
                del query_params[param]
        
        # Rebuild the URL without the problematic parameters
        if query_params:
            new_query = urlencode(query_params, doseq=True)
            DATABASE_URL = urlunparse(parsed_url._replace(query=new_query))
        else:
            DATABASE_URL = urlunparse(parsed_url._replace(query=None))

# Configure the async engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    connect_args = {"check_same_thread": False}
    engine = create_async_engine(
        DATABASE_URL,
        connect_args=connect_args,
        future=True,
        echo=True  # Enable SQL query logging for debugging
    )
else:
    # PostgreSQL configuration
    engine = create_async_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        future=True,
        echo=True  # Enable SQL query logging for debugging
    )

# Create async session factory
async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# For backward compatibility
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine.sync_engine if hasattr(engine, 'sync_engine') else engine
)
Base = declarative_base()

# Dependency
from typing import Generator

async def get_db() -> AsyncSession:
    """Dependency that provides an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e

# Initialize the database
async def init_db():
    """Initialize the database by creating all tables."""
    from ..database import models  # Import models to ensure they are registered with SQLAlchemy
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, bind=engine)
    print("Database tables created successfully")
