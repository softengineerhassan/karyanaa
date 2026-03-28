import sys
import os
import uuid
from sqlalchemy import select

# Add project root to sys.path
sys.path.append(os.getcwd())

import sys
from unittest.mock import MagicMock
sys.modules["boto3"] = MagicMock()
sys.modules["botocore"] = MagicMock()
sys.modules["botocore.exceptions"] = MagicMock()


from app.database.session import SessionLocal
from app.api.v1.schemas.user_schema import UserCreateRequest
from app.api.v1.actions.users_actions import UsersActions
from app.models.role import Role, UserRole
from app.models.user import User

def verify_user_creation():
    db = SessionLocal()
    try:
        # 1. Get or Create a Role
        role = db.execute(select(Role).limit(1)).scalar_one_or_none()
        if not role:
            print("No role found, creating a test role...")
            role = Role(name="test_role_" + str(uuid.uuid4())[:8])
            db.add(role)
            db.commit()
            db.refresh(role)
        
        print(f"Using Role ID: {role.id}")

        # 2. Create User Data
        email = f"test_user_{uuid.uuid4()}@example.com"
        user_data = UserCreateRequest(
            email=email,
            password="SecurePassword123!",
            full_name="Test User",
            role_id=role.id,
            is_active=True,
            is_superuser=False
        )

        # 3. Call Actions
        print(f"Creating user with email: {email}")
        response = UsersActions.create_user(user_data, db)
        
        # 4. Verify Response (response is a dict from Actions, data is Pydantic model)
        if not response.get("success"):
            print(f"FAILED: User creation failed. Response: {response}")
            return False
        
        created_user = response.get("data")
        # Check if created_user is a dict or a Pydantic model
        role_id_val = created_user.get("role_id") if isinstance(created_user, dict) else created_user.role_id

        if str(role_id_val) != str(role.id):
            print(f"FAILED: role_id mismatch in response. Expected {role.id}, got {role_id_val}")
            return False

        print("User created successfully via API Action, role_id verified in response.")


        # 5. Verify Database State
        # Clear session to ensure no stale objects are tracked
        db.expunge_all()
        
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not user:
             print("FAILED: User not found in database.")
             return False
        
        user_role = db.execute(select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id)).scalar_one_or_none()
        if not user_role:
             print("FAILED: UserRole association not found in database.")
             return False
        
        print("SUCCESS: User and UserRole verified in database.")

        # 6. Verify Update (Role Update)
        print("Testing User Update with Role Change...")
        # Create another role
        new_role_id = uuid.uuid4()
        new_role = Role(id=new_role_id, name="test_role_update_" + str(new_role_id)[:8])
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        
        # Clear session again and get clean user reference for update
        db.expunge_all()
        user_for_update = db.execute(select(User).where(User.id == user.id)).scalar_one_or_none()

        
        from app.api.v1.schemas.user_schema import UserUpdateRequest
        update_data = UserUpdateRequest(role_id=new_role.id)
        
        update_response = UsersActions.update_user(user_for_update.id, update_data, db)
        if not update_response.get("success"):
             print(f"FAILED: User update failed. Response: {update_response}")
             return False
        
        updated_user = update_response.get("data")
        updated_role_id_val = updated_user.get("role_id") if isinstance(updated_user, dict) else updated_user.role_id

        if str(updated_role_id_val) != str(new_role.id):
             print(f"FAILED: role_id update mismatch in response. Expected {new_role.id}, got {updated_role_id_val}")
             return False
        
        # Verify DB for update
        new_user_role = db.execute(select(UserRole).where(UserRole.user_id == user_for_update.id, UserRole.role_id == new_role.id)).scalar_one_or_none()
        if not new_user_role:
             print("FAILED: New UserRole association not found in database after update.")
             return False
        
        old_user_role = db.execute(select(UserRole).where(UserRole.user_id == user_for_update.id, UserRole.role_id == role.id)).scalar_one_or_none()
        if old_user_role:
             print("FAILED: Old UserRole association still exists in database after update.")
             return False

        print("SUCCESS: User update verified.")

        # Cleanup
        db.delete(new_user_role)
        db.delete(user_for_update)
        db.delete(new_role)
        
        # Cleanup
        db.delete(user_role)
        db.delete(user)
        db.commit()
        print("Cleanup complete.")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if verify_user_creation():
        sys.exit(0)
    else:
        sys.exit(1)
