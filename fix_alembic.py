import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def fix_alembic_version():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )
        cur = conn.cursor()
        
        new_version = '3e455169e798'
        print(f"Updating alembic_version to {new_version}...")
        cur.execute("DELETE FROM alembic_version;")
        cur.execute("INSERT INTO alembic_version (version_num) VALUES (%s);", (new_version,))
        
        conn.commit()
        cur.close()
        conn.close()
        print("Alembic version updated successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_alembic_version()
