# from typing import Generator
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy.pool import NullPool
# from app.core.config import settings

# # Convert async database URL to sync if needed (replace asyncpg with psycopg2, aiosqlite with sqlite)
# DATABASE_URL = settings.DATABASE_URL
# if not DATABASE_URL:
#     raise ValueError("Database URL not configured. Please set DATABASE_URL in your environment variables or .env file.")

# if DATABASE_URL.startswith("postgresql+asyncpg://"):
#     DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
# if DATABASE_URL.startswith("sqlite+aiosqlite://"):
#     DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")

# engine = create_engine(
#     DATABASE_URL,
#     echo=settings.DB_ECHO,
#     pool_size=settings.DB_POOL_SIZE,
#     max_overflow=settings.DB_MAX_OVERFLOW,
#     pool_timeout=settings.DB_POOL_TIMEOUT,
#     pool_pre_ping=True,
# )

# test_engine = create_engine(
#     DATABASE_URL,
#     echo=settings.DB_ECHO,
#     poolclass=NullPool,
# )

# SessionLocal = sessionmaker(
#     bind=engine,
#     autocommit=False,
#     autoflush=False,
#     expire_on_commit=False,
# )


# def get_db() -> Generator[Session, None, None]:
#     session = SessionLocal()
#     try:
#         yield session
#         session.commit()
#     except Exception:
#         session.rollback()
#         raise
#     finally:
#         session.close()


# def init_db() -> None:
#     with engine.connect() as conn:
#         # Use sqlalchemy.text to create an executable SQL expression
#         conn.execute(text("SELECT 1"))


# def close_db() -> None:
#     engine.dispose()

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from app.core.config import settings


DATABASE_URL = settings.DATABASE_URL

# -------------------------------
# Engine creation (ENV aware)
# -------------------------------

if settings.ENVIRONMENT == "test":
    # SQLite (CI / pytest)
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
else:
    # PostgreSQL (dev / prod)
    engine = create_engine(
        DATABASE_URL,
        echo=getattr(settings, "DATABASE_ECHO", False),
        pool_size=getattr(settings, "DATABASE_POOL_SIZE", 10),
        max_overflow=getattr(settings, "DATABASE_MAX_OVERFLOW", 5),
        pool_timeout=getattr(settings, "DATABASE_POOL_TIMEOUT", 30),
        pool_recycle=getattr(settings, "DATABASE_POOL_RECYCLE", 1800),
        pool_pre_ping=True,
    )


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# -------------------------------
# Dependency
# -------------------------------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# -------------------------------
# Lifecycle helpers
# -------------------------------
def init_db() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def close_db() -> None:
    engine.dispose()
