# from logging.config import fileConfig
# import os

# from sqlalchemy import engine_from_config, pool
# from alembic import context
# from dotenv import load_dotenv

# load_dotenv()

# # Alembic Config object
# config = context.config

# # Logging
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# # Import Base metadata
# from app.models.base import Base
# import app.models  # 🔥 THIS LINE IS REQUIRED
# target_metadata = Base.metadata

# # Determine SYNC database URL (env override or derive from app settings)
# DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")
# if not DATABASE_URL_SYNC:
#     try:
#         # Try to derive from application settings
#         from app.core.config import settings
#         DATABASE_URL_SYNC = settings.DATABASE_URL
#         # Convert async/special URLs to sync equivalents when necessary
#         if DATABASE_URL_SYNC and DATABASE_URL_SYNC.startswith("postgresql+asyncpg://"):
#             DATABASE_URL_SYNC = DATABASE_URL_SYNC.replace("postgresql+asyncpg://", "postgresql://")
#         if DATABASE_URL_SYNC and DATABASE_URL_SYNC.startswith("sqlite+aiosqlite://"):
#             DATABASE_URL_SYNC = DATABASE_URL_SYNC.replace("sqlite+aiosqlite://", "sqlite://")
#     except Exception:
#         # If settings cannot be loaded, fall through to raise below
#         DATABASE_URL_SYNC = None

# if not DATABASE_URL_SYNC:
#     raise RuntimeError("DATABASE_URL_SYNC is not set")

# config.set_main_option("sqlalchemy.url", DATABASE_URL_SYNC)


# def run_migrations_online():
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection,
#             target_metadata=target_metadata,
#             compare_type=True,
#         )

#         with context.begin_transaction():
#             context.run_migrations()


# run_migrations_online()






















from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from sqlalchemy import text  # ✅ add
from alembic import context
from dotenv import load_dotenv

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models.base import Base
import app.models
target_metadata = Base.metadata

DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")
if not DATABASE_URL_SYNC:
    try:
        from app.core.config import settings
        DATABASE_URL_SYNC = settings.DATABASE_URL
        if DATABASE_URL_SYNC and DATABASE_URL_SYNC.startswith("postgresql+asyncpg://"):
            DATABASE_URL_SYNC = DATABASE_URL_SYNC.replace("postgresql+asyncpg://", "postgresql://")
        if DATABASE_URL_SYNC and DATABASE_URL_SYNC.startswith("sqlite+aiosqlite://"):
            DATABASE_URL_SYNC = DATABASE_URL_SYNC.replace("sqlite+aiosqlite://", "sqlite://")
    except Exception:
        DATABASE_URL_SYNC = None

if not DATABASE_URL_SYNC:
    raise RuntimeError("DATABASE_URL_SYNC is not set")

config.set_main_option("sqlalchemy.url", DATABASE_URL_SYNC)


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # ✅ Force schema always
        connection.execute(text("SET search_path TO omnia"))

        # Set the target metadata schema so autogenerate includes it
        target_metadata.schema = "omnia"

        def include_object(object, name, type_, reflected, compare_to):
            # Ignore system tables or tables not in our target schemas
            if type_ == "table" and name in ["spatial_ref_sys", "alembic_version"]:
                return False
            return True

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=True,
            version_table_schema="omnia",
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
