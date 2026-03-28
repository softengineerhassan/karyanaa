import sys
import os
from sqlalchemy import text

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.database.session import engine

def add_joined_date_column():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS joined_date TIMESTAMP WITH TIME ZONE DEFAULT NULL;"))
            conn.commit()
            print("Successfully added joined_date column to users table.")
        except Exception as e:
            print(f"Error adding column: {e}")
            sys.exit(1)

if __name__ == "__main__":
    add_joined_date_column()
