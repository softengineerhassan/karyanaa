import sys
import os
import uuid
import datetime
from sqlalchemy import select, update

# Add project root to sys.path
sys.path.append(os.getcwd())

import sys
from unittest.mock import MagicMock
sys.modules["boto3"] = MagicMock()
sys.modules["botocore"] = MagicMock()
sys.modules["botocore.exceptions"] = MagicMock()

from app.database.session import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.core import security

def verify_joined_date():
    db = SessionLocal()
    try:
        # 1. Setup Data
        role = db.execute(select(Role).limit(1)).scalar_one_or_none()
        if not role:
            print("No role found, creating a test role...")
            role = Role(name="test_role_" + str(uuid.uuid4())[:8])
            db.add(role)
            db.commit()
            db.refresh(role)
        
        email = f"test_joined_{uuid.uuid4()}@example.com"
        password = "SecurePassword123!"
        hashed_pw = security.hash_password(password)
        
        # Create User manually via repo to ensure joined_date is NULL initially
        user = User(
            email=email,
            hashed_password=hashed_pw,
            full_name="Joined Date Test",
            is_active=True,
            is_superuser=False,
            joined_date=None  # Explicitly None
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"User created with ID: {user.id}")
        if user.joined_date is not None:
             print("FAILED: joined_date should be None initially.")
             return False

        # 2. Perform Login
        from app.services.auth_service import AuthService
        auth_service = AuthService(db)
        print("Logging in...")
        auth_service.login(email, password)
        
        # 3. Verify joined_date is set
        db.refresh(user)
        if user.joined_date is None:
             print("FAILED: joined_date should be set after first login.")
             return False
        
        first_joined_date = user.joined_date
        print(f"Joined date set to: {first_joined_date}")

        # 4. Perform Login Again
        print("Logging in again...")
        auth_service.login(email, password)
        
        db.refresh(user)
        if user.joined_date != first_joined_date:
             print(f"FAILED: joined_date changed on second login. Old: {first_joined_date}, New: {user.joined_date}")
             return False
        
        print("SUCCESS: joined_date verification passed.")
        
        # Cleanup
        db.delete(user)
        db.commit()
        
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if verify_joined_date():
        sys.exit(0)
    else:
        sys.exit(1)
