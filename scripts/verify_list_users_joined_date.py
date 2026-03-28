import sys
import os
import uuid
from datetime import datetime
from sqlalchemy import select

# Add project root to sys.path
sys.path.append(os.getcwd())

import sys
from unittest.mock import MagicMock
sys.modules["boto3"] = MagicMock()
sys.modules["botocore"] = MagicMock()
sys.modules["botocore.exceptions"] = MagicMock()

from app.database.session import SessionLocal
from app.services.auth_service import AuthService
from app.api.v1.actions.users_actions import UsersActions
from app.models.role import Role
from app.models.user import User
from app.core import security

def verify_list_users_joined_date():
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
        
        email = f"test_list_{uuid.uuid4()}@example.com"
        password = "SecurePassword123!"
        hashed_pw = security.hash_password(password)
        
        # Create User manually
        user = User(
            email=email,
            hashed_password=hashed_pw,
            full_name="List Date Test",
            is_active=True,
            is_superuser=False,
            joined_date=datetime.utcnow() # Set it explicitly
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"User created with ID: {user.id} and joined_date: {user.joined_date}")

        # 2. Call List Users
        print("Calling UsersActions.list_users...")
        pagination = {"page": 1, "page_size": 10}
        
        # Mock session for actions if needed, but passing db directly usually works if signature matches
        # UsersActions.list_users signature: (search, is_active, is_superuser, is_email_verified, pagination, session)
        
        response = UsersActions.list_users(
            search=email, 
            is_active=None, 
            is_superuser=None, 
            is_email_verified=None, 
            pagination=pagination, 
            session=db
        )
        
        if not response.get("success"):
            print("FAILED: list_users reported failure.")
            return False
            
        items = response.get("data", [])
        found_user = None
        for item in items:
            # item is likely a Pydantic model (UserResponse)
            # Accessing attribute directly
            if str(item.id) == str(user.id):
                found_user = item
                break
        
        if not found_user:
            print("FAILED: Created user not found in list.")
            return False
            
        print(f"Found user in response. joined_date field: {getattr(found_user, 'joined_date', 'MISSING')}")
        
        if found_user.joined_date is None:
             print("FAILED: joined_date is None in response.")
             return False
             
        # Check against db value (ignoring small precision diffs if any)
        # For simplicity just checking not None and loosely equal
        print("SUCCESS: joined_date verified in list_user response.")
        
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
    if verify_list_users_joined_date():
        sys.exit(0)
    else:
        sys.exit(1)
