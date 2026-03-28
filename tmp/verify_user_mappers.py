import sys
import os
from uuid import UUID

# Add the parent directory to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.v1.mappers.user_mapper import (
    map_user_to_current_user_response,
    map_user_to_public_response,
    map_user_to_user_response
)
from app.models.user import User
from datetime import datetime

# Logic verification without DB first
def verify_mappers():
    print("Verifying Mappers...")
    mock_user = User(
        id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="test@example.com",
        full_name="Test User",
        phone_number="+123456789",
        location="Test City",
        is_active=True,
        is_superuser=False,
        is_email_verified=True,
        created_at=datetime.utcnow()
    )

    # 1. current_user_response
    print("Testing map_user_to_current_user_response...")
    current_resp = map_user_to_current_user_response(mock_user)
    print(f"Current User Response: phone={current_resp.phone_number}, location={current_resp.location}")
    assert current_resp.phone_number == "+123456789"
    assert current_resp.location == "Test City"

    # 2. public_response
    print("\nTesting map_user_to_public_response...")
    public_resp = map_user_to_public_response(mock_user)
    print(f"Public User Response: phone={public_resp.phone_number}, location={public_resp.location}")
    assert public_resp.phone_number == "+123456789"
    assert public_resp.location == "Test City"

    # 3. user_response
    print("\nTesting map_user_to_user_response...")
    user_resp = map_user_to_user_response(mock_user)
    print(f"User Response: phone={user_resp.phone_number}, location={user_resp.location}")
    assert user_resp.phone_number == "+123456789"
    assert user_resp.location == "Test City"

    print("\nSUCCESS: All mappers verified correctly!")

if __name__ == "__main__":
    verify_mappers()
