"""Permission constants for RBAC system."""

# User permissions
USERS_CREATE = "users:create"
USERS_READ = "users:read"
USERS_UPDATE = "users:update"
USERS_DELETE = "users:delete"
USERS_LIST = "users:list"

# Role permissions
ROLES_CREATE = "roles:create"
ROLES_READ = "roles:read"
ROLES_UPDATE = "roles:update"
ROLES_DELETE = "roles:delete"
ROLES_LIST = "roles:list"

# Permission permissions
PERMISSIONS_CREATE = "permissions:create"
PERMISSIONS_READ = "permissions:read"
PERMISSIONS_UPDATE = "permissions:update"
PERMISSIONS_DELETE = "permissions:delete"
PERMISSIONS_LIST = "permissions:list"

# Auth permissions
AUTH_REGISTER = "auth:register"
AUTH_LOGIN = "auth:login"
AUTH_LOGOUT = "auth:logout"
AUTH_REFRESH = "auth:refresh"
AUTH_PROFILE_READ = "auth:profile:read"
AUTH_PROFILE_UPDATE = "auth:profile:update"

# Admin permissions
ADMIN_ALL = "admin:all"  # Super admin permission

# Role-based permission sets
USER_PERMISSIONS = [
    AUTH_LOGIN,
    AUTH_LOGOUT,
    AUTH_REFRESH,
    AUTH_PROFILE_READ,
    AUTH_PROFILE_UPDATE,
    USERS_READ,  # Can read own profile
]

ADMIN_PERMISSIONS = [
    # All user permissions
    *USER_PERMISSIONS,
    # User management
    USERS_CREATE,
    USERS_UPDATE,
    USERS_DELETE,
    USERS_LIST,
    # Role management (read only)
    ROLES_READ,
    ROLES_LIST,
    # Permission management (read only)
    PERMISSIONS_READ,
    PERMISSIONS_LIST,
]

SUPER_ADMIN_PERMISSIONS = [
    ADMIN_ALL,  # Has all permissions
]

# Map role names to permissions
ROLE_PERMISSIONS_MAP = {
    "user": USER_PERMISSIONS,
    "admin": ADMIN_PERMISSIONS,
    "super_admin": SUPER_ADMIN_PERMISSIONS,
}


def get_permissions_for_role(role_name: str) -> list[str]:
    """Get permissions for a given role name."""
    return ROLE_PERMISSIONS_MAP.get(role_name.lower(), [])


def has_permission(user_permissions: list[str], required_permission: str) -> bool:
    """
    Check if user has a specific permission.
    Super admin (with admin:all) has all permissions.
    """
    if ADMIN_ALL in user_permissions:
        return True
    return required_permission in user_permissions


def has_any_permission(
    user_permissions: list[str], required_permissions: list[str]
) -> bool:
    """
    Check if user has any of the required permissions.
    Super admin (with admin:all) has all permissions.
    """
    if ADMIN_ALL in user_permissions:
        return True
    return any(perm in user_permissions for perm in required_permissions)


def has_all_permissions(
    user_permissions: list[str], required_permissions: list[str]
) -> bool:
    """
    Check if user has all of the required permissions.
    Super admin (with admin:all) has all permissions.
    """
    if ADMIN_ALL in user_permissions:
        return True
    return all(perm in user_permissions for perm in required_permissions)
