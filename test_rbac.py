#!/usr/bin/env python3
"""Test script for RBAC implementation."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import Settings
from auth.domain.entities.permission import Permission
from auth.domain.entities.role import Role
from auth.domain.entities.user import User
from auth.infra.mongodb.permission_repository import MongoPermissionRepository
from auth.infra.mongodb.role_repository import MongoRoleRepository
from auth.infra.mongodb.user_repository import MongoUserRepository
from auth.infra.security.bcrypt_hasher import BcryptPasswordHasher
from auth.infra.security.jwt_generator import JWTTokenGenerator
from auth.constants import (
    USERS_CREATE,
    USERS_READ,
    ADMIN_ALL,
    has_permission,
    has_any_permission,
)


async def test_rbac():
    """Test RBAC functionality."""
    print("=" * 60)
    print("RBAC System Test")
    print("=" * 60 + "\n")

    # Setup
    settings = Settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.mongodb_database]

    permission_repo = MongoPermissionRepository(database)
    role_repo = MongoRoleRepository(database)
    user_repo = MongoUserRepository(database)
    password_hasher = BcryptPasswordHasher()
    token_generator = JWTTokenGenerator(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )

    try:
        # Test 1: Permission Creation
        print("Test 1: Permission Creation")
        test_perm = Permission(
            name="test:action",
            description="Test permission",
            resource="test",
            action="action",
        )
        # Check if exists first
        existing_perm = await permission_repo.get_by_name("test:action")
        if existing_perm:
            print("  ✓ Permission already exists")
            test_perm = existing_perm
        else:
            test_perm = await permission_repo.create(test_perm)
            print(f"  ✓ Created permission: {test_perm.name} (ID: {test_perm.id})")

        # Test 2: Role Creation
        print("\nTest 2: Role Creation")
        test_role = await role_repo.get_by_name("test_role")
        if test_role:
            print("  ✓ Role already exists")
        else:
            test_role = Role(
                name="test_role",
                description="Test role",
                permission_ids=[test_perm.id],
                is_system=False,
            )
            test_role = await role_repo.create(test_role)
            print(f"  ✓ Created role: {test_role.name} (ID: {test_role.id})")

        # Test 3: User with Role
        print("\nTest 3: User with Role and Permissions")
        test_user = await user_repo.get_by_email("test@example.com")
        if test_user:
            print("  ✓ Test user already exists")
        else:
            hashed_pass = password_hasher.hash_password("testpass123")
            test_user = User(
                email="test@example.com",
                hashed_password=hashed_pass,
                full_name="Test User",
                is_active=True,
                is_verified=True,
                role_id=test_role.id,
                permissions=["test:action"],
            )
            test_user = await user_repo.create(test_user)
            print(f"  ✓ Created user: {test_user.email}")
            print(f"    - Role ID: {test_user.role_id}")
            print(f"    - Permissions: {test_user.permissions}")

        # Test 4: JWT Token with Permissions
        print("\nTest 4: JWT Token with Permissions")
        access_token = token_generator.generate_access_token(
            user_id=test_user.id,
            email=test_user.email,
            permissions=test_user.permissions,
        )
        print(f"  ✓ Generated access token")

        # Decode and verify
        token_data = token_generator.decode_token(access_token)
        print(f"    - User ID: {token_data.user_id}")
        print(f"    - Email: {token_data.email}")
        print(f"    - Permissions: {token_data.permissions}")

        # Test 5: Permission Checking
        print("\nTest 5: Permission Checking Functions")

        # Test has_permission
        result = has_permission(token_data.permissions, "test:action")
        print(f"  ✓ has_permission('test:action'): {result}")
        assert result == True, "Should have test:action permission"

        result = has_permission(token_data.permissions, "test:other")
        print(f"  ✓ has_permission('test:other'): {result}")
        assert result == False, "Should not have test:other permission"

        # Test has_any_permission
        result = has_any_permission(
            token_data.permissions, ["test:action", "other:action"]
        )
        print(f"  ✓ has_any_permission(['test:action', 'other:action']): {result}")
        assert result == True, "Should have at least one permission"

        # Test 6: Super Admin Permissions
        print("\nTest 6: Super Admin Bypass")
        super_admin = await user_repo.get_by_email("superadmin@example.com")
        if super_admin:
            print(f"  ✓ Found super admin: {super_admin.email}")
            print(f"    - Permissions: {super_admin.permissions}")

            # Super admin should have admin:all
            result = has_permission(super_admin.permissions, ADMIN_ALL)
            print(f"  ✓ Has admin:all: {result}")

            # Super admin should pass any permission check
            result = has_permission(super_admin.permissions, USERS_CREATE)
            print(f"  ✓ Can create users (via admin:all): {result}")

        # Test 7: List All Roles
        print("\nTest 7: List All Roles")
        all_roles = await role_repo.list_all()
        print(f"  ✓ Found {len(all_roles)} roles:")
        for role in all_roles:
            print(f"    - {role.name}: {len(role.permission_ids)} permissions")

        # Test 8: List All Permissions
        print("\nTest 8: List All Permissions")
        all_permissions = await permission_repo.list_all()
        print(f"  ✓ Found {len(all_permissions)} permissions")
        print("  Sample permissions:")
        for perm in all_permissions[:5]:
            print(f"    - {perm.name}: {perm.description}")

        print("\n" + "=" * 60)
        print("✓ All RBAC tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(test_rbac())
