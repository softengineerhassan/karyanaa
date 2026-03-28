import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def main() -> None:
    load_dotenv()
    db_url = os.getenv("DATABASE_URL_SYNC")
    if not db_url:
        raise RuntimeError("DATABASE_URL_SYNC is not set")

    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS karyanaa CASCADE"))
        conn.execute(text("CREATE SCHEMA karyanaa"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        # Clear any stray alembic table in public from previous runs.
        conn.execute(text("DROP TABLE IF EXISTS public.alembic_version"))

    print("RESET_OK")


if __name__ == "__main__":
    main()
