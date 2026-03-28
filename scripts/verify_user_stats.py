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
from app.repos.user_repository import UserRepository
from app.core import security


def verify_user_stats():
    """Verify that list_users endpoint returns correct statistics"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Verifying User Statistics in List Users Response")
        print("=" * 60)
        
        # Track created users and roles for cleanup
        created_users = []
        created_roles = []
        
        # 1. Get or Create Vendor Role
        vendor_role = db.execute(select(Role).where(Role.name == "vendor")).scalar_one_or_none()
        if not vendor_role:
            print("Creating vendor role...")
            vendor_role = Role(name="vendor", description="Vendor role")
            db.add(vendor_role)
            db.commit()
            db.refresh(vendor_role)
            created_roles.append(vendor_role)
        print(f"Using Vendor Role ID: {vendor_role.id}")
        
        # 2. Get or Create a Non-Vendor Role
        admin_role = db.execute(select(Role).where(Role.name == "admin")).scalar_one_or_none()
        if not admin_role:
            print("Creating admin role...")
            admin_role = Role(name="admin", description="Admin role")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            created_roles.append(admin_role)
        print(f"Using Admin Role ID: {admin_role.id}")
        
        # 3. Get initial counts (before creating test users)
        user_repo = UserRepository(db)
        initial_total = user_repo.count_total_users()
        initial_active = user_repo.count_active_users()
        initial_inactive = user_repo.count_inactive_users()
        initial_vendors = user_repo.count_vendors()
        
        print(f"\nInitial counts:")
        print(f"  Total users: {initial_total}")
        print(f"  Active users: {initial_active}")
        print(f"  Inactive users: {initial_inactive}")
        print(f"  Vendors: {initial_vendors}")
        
        # 4. Create test users
        print("\nCreating test users...")
        
        # Create active vendor user
        active_vendor_email = f"active_vendor_{uuid.uuid4()}@example.com"
        active_vendor_data = UserCreateRequest(
            email=active_vendor_email,
            password="SecurePassword123!",
            full_name="Active Vendor User",
            role_id=vendor_role.id,
            is_active=True,
            is_superuser=False
        )
        active_vendor_response = UsersActions.create_user(active_vendor_data, db)
        if active_vendor_response.get("success"):
            created_users.append(active_vendor_email)
            print(f"  ✓ Created active vendor: {active_vendor_email}")
        
        # Create inactive vendor user
        inactive_vendor_email = f"inactive_vendor_{uuid.uuid4()}@example.com"
        inactive_vendor_data = UserCreateRequest(
            email=inactive_vendor_email,
            password="SecurePassword123!",
            full_name="Inactive Vendor User",
            role_id=vendor_role.id,
            is_active=False,
            is_superuser=False
        )
        inactive_vendor_response = UsersActions.create_user(inactive_vendor_data, db)
        if inactive_vendor_response.get("success"):
            created_users.append(inactive_vendor_email)
            print(f"  ✓ Created inactive vendor: {inactive_vendor_email}")
        
        # Create active non-vendor user
        active_admin_email = f"active_admin_{uuid.uuid4()}@example.com"
        active_admin_data = UserCreateRequest(
            email=active_admin_email,
            password="SecurePassword123!",
            full_name="Active Admin User",
            role_id=admin_role.id,
            is_active=True,
            is_superuser=False
        )
        active_admin_response = UsersActions.create_user(active_admin_data, db)
        if active_admin_response.get("success"):
            created_users.append(active_admin_email)
            print(f"  ✓ Created active admin: {active_admin_email}")
        
        # Create inactive non-vendor user
        inactive_admin_email = f"inactive_admin_{uuid.uuid4()}@example.com"
        inactive_admin_data = UserCreateRequest(
            email=inactive_admin_email,
            password="SecurePassword123!",
            full_name="Inactive Admin User",
            role_id=admin_role.id,
            is_active=False,
            is_superuser=False
        )
        inactive_admin_response = UsersActions.create_user(inactive_admin_data, db)
        if inactive_admin_response.get("success"):
            created_users.append(inactive_admin_email)
            print(f"  ✓ Created inactive admin: {inactive_admin_email}")
        
        # 5. Get expected counts
        expected_total = initial_total + 4
        expected_active = initial_active + 2  # active_vendor + active_admin
        expected_inactive = initial_inactive + 2  # inactive_vendor + inactive_admin
        expected_vendors = initial_vendors + 2  # active_vendor + inactive_vendor
        
        print(f"\nExpected counts after creating test users:")
        print(f"  Total users: {expected_total}")
        print(f"  Active users: {expected_active}")
        print(f"  Inactive users: {expected_inactive}")
        print(f"  Vendors: {expected_vendors}")
        
        # 6. Call list_users endpoint
        print("\nCalling list_users endpoint...")
        pagination = {
            "page": 1,
            "page_size": 20,
            "offset": 0,
            "limit": 20
        }
        
        response = UsersActions.list_users(
            search=None,
            is_active=None,
            is_superuser=None,
            is_email_verified=None,
            pagination=pagination,
            session=db
        )
        
        # 7. Verify response structure
        print("\nVerifying response structure...")
        
        # Check if response is a Pydantic model or dict
        if hasattr(response, 'stats'):
            # Pydantic model
            stats = response.stats
            response_data = response.data
            response_meta = response.meta
            response_success = response.success
            response_message = response.message
        elif isinstance(response, dict):
            # Dict response
            stats = response.get("stats")
            response_data = response.get("data")
            response_meta = response.get("meta")
            response_success = response.get("success")
            response_message = response.get("message")
        else:
            print(f"FAILED: Unexpected response type: {type(response)}")
            print(f"Response: {response}")
            return False
        
        if stats is None:
            print("FAILED: 'stats' field is missing from response")
            return False
        
        print("  ✓ Response has 'stats' field")
        
        # 8. Verify stats values
        print("\nVerifying stats values...")
        
        # Extract stats values (handle both dict and Pydantic model)
        if hasattr(stats, 'total_users'):
            actual_total = stats.total_users
            actual_active = stats.active_users
            actual_inactive = stats.inactive_users
            actual_vendors = stats.vendors
        elif isinstance(stats, dict):
            actual_total = stats.get("total_users")
            actual_active = stats.get("active_users")
            actual_inactive = stats.get("inactive_users")
            actual_vendors = stats.get("vendors")
        else:
            print(f"FAILED: Unexpected stats type: {type(stats)}")
            return False
        
        print(f"  Actual total_users: {actual_total}")
        print(f"  Actual active_users: {actual_active}")
        print(f"  Actual inactive_users: {actual_inactive}")
        print(f"  Actual vendors: {actual_vendors}")
        
        # Verify counts match expected values
        all_correct = True
        
        if actual_total != expected_total:
            print(f"  ✗ FAILED: total_users mismatch. Expected {expected_total}, got {actual_total}")
            all_correct = False
        else:
            print(f"  ✓ total_users correct: {actual_total}")
        
        if actual_active != expected_active:
            print(f"  ✗ FAILED: active_users mismatch. Expected {expected_active}, got {actual_active}")
            all_correct = False
        else:
            print(f"  ✓ active_users correct: {actual_active}")
        
        if actual_inactive != expected_inactive:
            print(f"  ✗ FAILED: inactive_users mismatch. Expected {expected_inactive}, got {actual_inactive}")
            all_correct = False
        else:
            print(f"  ✓ inactive_users correct: {actual_inactive}")
        
        if actual_vendors != expected_vendors:
            print(f"  ✗ FAILED: vendors mismatch. Expected {expected_vendors}, got {actual_vendors}")
            all_correct = False
        else:
            print(f"  ✓ vendors correct: {actual_vendors}")
        
        # 9. Verify response structure completeness
        print("\nVerifying response structure completeness...")
        if response_success is None:
            print("  ✗ FAILED: 'success' field is missing")
            all_correct = False
        else:
            print(f"  ✓ 'success' field present: {response_success}")
        
        if response_message is None:
            print("  ✗ FAILED: 'message' field is missing")
            all_correct = False
        else:
            print(f"  ✓ 'message' field present: {response_message}")
        
        if response_data is None:
            print("  ✗ FAILED: 'data' field is missing")
            all_correct = False
        else:
            print(f"  ✓ 'data' field present (list with {len(response_data)} items)")
        
        if response_meta is None:
            print("  ✗ FAILED: 'meta' field is missing")
            all_correct = False
        else:
            print(f"  ✓ 'meta' field present")
            if isinstance(response_meta, dict):
                print(f"    - total: {response_meta.get('total')}")
                print(f"    - page: {response_meta.get('page')}")
                print(f"    - page_size: {response_meta.get('page_size')}")
        
        # 10. Cleanup
        print("\nCleaning up test users...")
        for email in created_users:
            user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
            if user:
                # Delete user roles first
                user_roles = db.execute(select(UserRole).where(UserRole.user_id == user.id)).scalars().all()
                for ur in user_roles:
                    db.delete(ur)
                db.delete(user)
                print(f"  ✓ Deleted user: {email}")
        
        # Only delete roles if we created them
        for role in created_roles:
            db.delete(role)
            print(f"  ✓ Deleted role: {role.name}")
        
        db.commit()
        print("Cleanup complete.")
        
        # Final result
        print("\n" + "=" * 60)
        if all_correct:
            print("SUCCESS: All verifications passed!")
            print("=" * 60)
            return True
        else:
            print("FAILED: Some verifications failed.")
            print("=" * 60)
            return False
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if verify_user_stats():
        sys.exit(0)
    else:
        sys.exit(1)







