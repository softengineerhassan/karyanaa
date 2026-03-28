from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os


def main() -> None:
    load_dotenv()
    db_url = os.getenv("DATABASE_URL_SYNC")
    if not db_url:
        raise RuntimeError("DATABASE_URL_SYNC is not set")

    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS karyanaa"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        present = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'postgis'")
        ).fetchone()

    print("POSTGIS_PRESENT", bool(present))


if __name__ == "__main__":
    main()
