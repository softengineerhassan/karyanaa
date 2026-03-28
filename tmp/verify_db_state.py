from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os


def main() -> None:
    load_dotenv()
    db_url = os.getenv("DATABASE_URL_SYNC")
    if not db_url:
        raise RuntimeError("DATABASE_URL_SYNC is not set")

    engine = create_engine(db_url)
    with engine.connect() as conn:
        schemas = conn.execute(
            text("SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('karyanaa', 'omnia') ORDER BY schema_name")
        ).fetchall()
        postgis = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'postgis'")
        ).fetchone()
        versions = conn.execute(
            text("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name = 'alembic_version' ORDER BY table_schema")
        ).fetchall()
        karyanaa_tables = conn.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'karyanaa'")
        ).scalar_one()

    print("SCHEMAS", [s[0] for s in schemas])
    print("POSTGIS_PRESENT", bool(postgis))
    print("ALEMBIC_VERSION_TABLES", [(v[0], v[1]) for v in versions])
    print("KARYANAA_TABLE_COUNT", karyanaa_tables)


if __name__ == "__main__":
    main()
