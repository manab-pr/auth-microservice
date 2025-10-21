#!/usr/bin/env python3
"""Database seeder script for RBAC system."""
import asyncio
import json
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from config import Settings
from auth.domain.entities.permission import Permission
from auth.domain.entities.role import Role
from auth.domain.entities.user import User
from auth.infra.mongodb.permission_repository import MongoPermissionRepository
from auth.infra.mongodb.role_repository import MongoRoleRepository
from auth.infra.mongodb.user_repository import MongoUserRepository
from auth.infra.security.bcrypt_hasher import BcryptPasswordHasher


async def load_json_fixture(filename: str) -> list:
    """Load JSON fixture file."""
    fixture_path = Path(__file__).parent / "fixtures" / filename
    with open(fixture_path, "r") as f:
        return json.load(f)


async def seed_permissions(permission_repo: MongoPermissionRepository) -> dict:
    """Seed permissions and return mapping of name to ID."""
    print("Seeding permissions...")
    permissions_data = await load_json_fixture("permissions.json")
    permission_map = {}

    for perm_data in permissions_data:
        # Check if permission already exists
        existing = await permission_repo.get_by_name(perm_data["name"])
        if existing:
            print(f"  - Permission '{perm_data['name']}' already exists, skipping...")
            permission_map[perm_data["name"]] = existing.id
            continue

        # Create new permission
        permission = Permission(
            name=perm_data["name"],
            description=perm_data["description"],
            resource=perm_data["resource"],
            action=perm_data["action"],
        )
        created = await permission_repo.create(permission)
        permission_map[perm_data["name"]] = created.id
        print(f"  ✓ Created permission: {perm_data['name']}")

    print(f"Permissions seeded: {len(permission_map)} total\n")
    return permission_map


async def seed_roles(
    role_repo: MongoRoleRepository, permission_map: dict
) -> dict:
    """Seed roles and return mapping of name to ID."""
    print("Seeding roles...")
    roles_data = await load_json_fixture("roles.json")
    role_map = {}

    for role_data in roles_data:
        # Check if role already exists
        existing = await role_repo.get_by_name(role_data["name"])
        if existing:
            print(f"  - Role '{role_data['name']}' already exists, skipping...")
            role_map[role_data["name"]] = existing.id
            continue

        # Map permission names to IDs
        permission_ids = [
            permission_map[perm_name] for perm_name in role_data["permissions"]
        ]

        # Create new role
        role = Role(
            name=role_data["name"],
            description=role_data["description"],
            permission_ids=permission_ids,
            is_system=role_data.get("is_system", False),
        )
        created = await role_repo.create(role)
        role_map[role_data["name"]] = created.id
        print(
            f"  ✓ Created role: {role_data['name']} ({len(permission_ids)} permissions)"
        )

    print(f"Roles seeded: {len(role_map)} total\n")
    return role_map


async def seed_users(
    user_repo: MongoUserRepository,
    role_repo: MongoRoleRepository,
    permission_repo: MongoPermissionRepository,
    password_hasher: BcryptPasswordHasher,
    role_map: dict,
) -> None:
    """Seed users with roles and permissions."""
    print("Seeding users...")
    users_data = await load_json_fixture("users.json")

    for user_data in users_data:
        # Check if user already exists
        existing = await user_repo.get_by_email(user_data["email"])
        if existing:
            print(f"  - User '{user_data['email']}' already exists, skipping...")
            continue

        # Get role
        role_name = user_data["role"]
        role_id = role_map.get(role_name)
        if not role_id:
            print(f"  ✗ Role '{role_name}' not found for user '{user_data['email']}'")
            continue

        # Get role details to load permissions
        role = await role_repo.get_by_id(role_id)
        permissions = await permission_repo.get_by_ids(role.permission_ids)
        permission_names = [perm.name for perm in permissions]

        # Hash password
        hashed_password = password_hasher.hash_password(user_data["password"])

        # Create user
        user = User(
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data["full_name"],
            is_active=user_data.get("is_active", True),
            is_verified=user_data.get("is_verified", False),
            role_id=role_id,
            permissions=permission_names,
        )
        await user_repo.create(user)
        print(
            f"  ✓ Created user: {user_data['email']} (role: {role_name}, {len(permission_names)} permissions)"
        )

    print(f"Users seeded successfully\n")


async def main():
    """Main seeder function."""
    print("=" * 60)
    print("FastAPI RBAC Database Seeder")
    print("=" * 60 + "\n")

    # Load settings
    settings = Settings()

    # Connect to MongoDB
    print(f"Connecting to MongoDB: {settings.mongodb_url}")
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.mongodb_database]
    print("✓ Connected to MongoDB\n")

    try:
        # Initialize repositories
        permission_repo = MongoPermissionRepository(database)
        role_repo = MongoRoleRepository(database)
        user_repo = MongoUserRepository(database)
        password_hasher = BcryptPasswordHasher()

        # Seed in order: permissions -> roles -> users
        permission_map = await seed_permissions(permission_repo)
        role_map = await seed_roles(role_repo, permission_map)
        await seed_users(user_repo, role_repo, permission_repo, password_hasher, role_map)

        print("=" * 60)
        print("✓ Seeding completed successfully!")
        print("=" * 60)
        print("\nTest Credentials:")
        print("  Regular User:")
        print("    Email: user@example.com")
        print("    Password: userpass123")
        print("\n  Admin:")
        print("    Email: admin@example.com")
        print("    Password: adminpass123")
        print("\n  Super Admin:")
        print("    Email: superadmin@example.com")
        print("    Password: superadminpass123")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during seeding: {str(e)}")
        raise
    finally:
        client.close()
        print("\n✓ MongoDB connection closed")


if __name__ == "__main__":
    asyncio.run(main())
