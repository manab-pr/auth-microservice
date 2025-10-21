# Role-Based Access Control (RBAC) Implementation

## Overview

This FastAPI authentication microservice now includes a comprehensive Role-Based Access Control (RBAC) system following clean architecture principles.

## Architecture

### Domain Layer
- **Entities**:
  - `Permission`: Represents an action (e.g., "users:create", "users:read")
  - `Role`: Collection of permissions (e.g., "user", "admin", "super_admin")
  - `User`: Updated to include `role_id` and `permissions` fields

- **Repositories (Ports)**:
  - `PermissionRepository`: CRUD operations for permissions
  - `RoleRepository`: CRUD operations for roles
  - `UserRepository`: Updated to handle role and permission fields

### Infrastructure Layer
- **MongoDB Implementations**:
  - `MongoPermissionRepository`: Permission storage in MongoDB
  - `MongoRoleRepository`: Role storage in MongoDB
  - Updated `MongoUserRepository`: Handles role_id and permissions

- **Security**:
  - Updated `JWTTokenGenerator`: Includes permissions in JWT tokens
  - Permissions embedded in both access and refresh tokens

### Presentation Layer
- **Dependencies**:
  - `get_current_user()`: Returns TokenData with permissions
  - `require_permissions(*perms)`: Dependency to check ALL required permissions
  - `require_any_permission(*perms)`: Dependency to check ANY required permission

## System Roles

### 1. User (Regular User)
**Permissions**:
- `auth:login` - Login to system
- `auth:logout` - Logout from system
- `auth:refresh` - Refresh access token
- `auth:profile:read` - Read own profile
- `auth:profile:update` - Update own profile
- `users:read` - Read user information

**Use Case**: Regular users with basic access to their own data

### 2. Admin
**Permissions**:
All user permissions plus:
- `users:create` - Create new users
- `users:update` - Update user information
- `users:delete` - Delete users
- `users:list` - List all users
- `roles:read` - Read role information
- `roles:list` - List all roles
- `permissions:read` - Read permission information
- `permissions:list` - List all permissions

**Use Case**: Administrators who can manage users and view roles/permissions

### 3. Super Admin
**Permissions**:
- `admin:all` - All permissions (wildcard)

**Use Case**: Super administrators with unrestricted access

## Permission Format

Permissions follow the `resource:action` pattern:
```
users:create
users:read
users:update
users:delete
users:list
roles:create
roles:read
...
```

## Setup and Seeding

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=fastapi_auth
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Run Database Seeder
```bash
python seeder.py
```

This will create:
- **22 Permissions** (all auth, user, role, and permission operations)
- **3 Roles** (user, admin, super_admin)
- **3 Test Users**:
  - `user@example.com` / `userpass123` (Regular User)
  - `admin@example.com` / `adminpass123` (Admin)
  - `superadmin@example.com` / `superadminpass123` (Super Admin)

## Usage Examples

### Protecting Routes with Permissions

#### Require Specific Permission
```python
from fastapi import APIRouter, Depends
from auth.presentation.http.dependencies import require_permissions
from auth.domain.services import TokenData
from auth.constants import USERS_LIST

router = APIRouter()

@router.get("/users")
async def list_users(
    current_user: TokenData = Depends(require_permissions(USERS_LIST))
):
    # Only users with "users:list" permission can access
    return {"message": "List of users"}
```

#### Require Multiple Permissions (ALL)
```python
from auth.constants import USERS_UPDATE, ROLES_UPDATE

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    current_user: TokenData = Depends(require_permissions(USERS_UPDATE, ROLES_UPDATE))
):
    # User must have BOTH permissions
    return {"message": f"User {user_id} updated"}
```

#### Require Any of Multiple Permissions
```python
from auth.presentation.http.dependencies import require_any_permission
from auth.constants import USERS_READ, ADMIN_ALL

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: TokenData = Depends(require_any_permission(USERS_READ, ADMIN_ALL))
):
    # User needs either "users:read" OR "admin:all"
    return {"message": f"User {user_id} details"}
```

### Manual Permission Checking

```python
from auth.constants import has_permission, USERS_DELETE

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    if not has_permission(current_user.permissions, USERS_DELETE):
        raise HTTPException(403, "Insufficient permissions")

    # Delete user logic
    return {"message": "User deleted"}
```

### Assigning Roles to Users

```python
from auth.domain.usecases.assign_role import AssignRoleUseCase

# In your handler
async def assign_role_to_user(user_id: str, role_id: str):
    assign_role_use_case = container.assign_role_use_case()
    await assign_role_use_case.execute(user_id, role_id)
```

## JWT Token Structure

Access and refresh tokens now include permissions:

```json
{
  "sub": "user_id_here",
  "email": "user@example.com",
  "permissions": [
    "auth:login",
    "auth:logout",
    "auth:profile:read",
    "users:read"
  ],
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "unique-token-id",
  "type": "access"
}
```

## Permission Loading Flow

1. **Registration**: User created without role (optional default role can be set)
2. **Role Assignment**: Admin assigns role to user via `AssignRoleUseCase`
3. **Permission Loading**: Use case loads all permissions from role and stores in user.permissions
4. **Login**: Permissions included in JWT token
5. **Request**: Middleware validates token and extracts permissions
6. **Authorization**: Permission guards check if user has required permissions

## Database Collections

### permissions
```javascript
{
  _id: ObjectId,
  name: "users:create",
  description: "Create new users",
  resource: "users",
  action: "create",
  created_at: ISODate,
  updated_at: ISODate
}
```

### roles
```javascript
{
  _id: ObjectId,
  name: "admin",
  description: "Administrator role",
  permission_ids: [ObjectId, ObjectId, ...],
  is_system: true,
  created_at: ISODate,
  updated_at: ISODate
}
```

### users
```javascript
{
  _id: ObjectId,
  email: "user@example.com",
  hashed_password: "...",
  full_name: "User Name",
  is_active: true,
  is_verified: true,
  role_id: ObjectId,
  permissions: ["auth:login", "users:read", ...],
  created_at: ISODate,
  updated_at: ISODate
}
```

## Testing the RBAC System

### 1. Start the Server
```bash
uvicorn main:app --reload
```

### 2. Login as Different Users

**Regular User**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "userpass123"}'
```

**Admin**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "adminpass123"}'
```

**Super Admin**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "superadmin@example.com", "password": "superadminpass123"}'
```

### 3. Decode JWT Token
Use jwt.io or decode programmatically to see permissions in token.

### 4. Access Protected Routes
```bash
curl -X GET http://localhost:8000/protected-route \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Advanced Features

### Super Admin Bypass
Users with `admin:all` permission automatically pass all permission checks:
```python
if ADMIN_ALL in current_user.permissions:
    return current_user  # Bypass all checks
```

### Dynamic Permission Checking
```python
from auth.constants import has_any_permission

if has_any_permission(user.permissions, ["users:update", "admin:all"]):
    # User can update
    pass
```

### Role Hierarchy
While not implemented directly, you can create role hierarchies by:
1. Creating roles with overlapping permissions
2. Assigning more permissive roles to senior users

## File Structure
```
fastapi/
├── auth/
│   ├── constants/
│   │   ├── __init__.py
│   │   └── permissions.py          # Permission constants
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── permission.py
│   │   │   ├── role.py
│   │   │   └── user.py             # Updated with RBAC fields
│   │   ├── ports/
│   │   │   ├── permission_repository.py
│   │   │   └── role_repository.py
│   │   └── usecases/
│   │       ├── assign_role.py
│   │       ├── list_roles.py
│   │       └── list_permissions.py
│   ├── infra/
│   │   ├── mongodb/
│   │   │   ├── permission_repository.py
│   │   │   ├── role_repository.py
│   │   │   └── user_repository.py  # Updated
│   │   └── security/
│   │       └── jwt_generator.py    # Updated with permissions
│   ├── presentation/
│   │   └── http/
│   │       └── dependencies.py     # Permission guards
│   └── container.py                # Updated with RBAC deps
├── fixtures/
│   ├── permissions.json
│   ├── roles.json
│   └── users.json
├── seeder.py
└── RBAC_README.md
```

## Security Best Practices

1. **Never Store Permissions in Client**: Permissions in JWT are for server-side validation only
2. **Use HTTPS in Production**: Protect JWT tokens in transit
3. **Rotate Secrets Regularly**: Change JWT_SECRET_KEY periodically
4. **Audit Permission Changes**: Log all role/permission modifications
5. **Principle of Least Privilege**: Grant minimum permissions needed
6. **Review Roles Regularly**: Audit role assignments quarterly

## Troubleshooting

### User Has No Permissions After Login
- Check if user has a role assigned
- Verify role has permissions
- Re-assign role to reload permissions

### Permission Denied Despite Correct Role
- Decode JWT to verify permissions are in token
- Check if permission constant matches exactly
- Verify super_admin has `admin:all` permission

### Seeder Fails
- Ensure MongoDB is running
- Check database connection string
- Verify fixtures files are valid JSON

## Next Steps

1. **Add Permission Management Endpoints**: CRUD operations for permissions
2. **Add Role Management Endpoints**: CRUD operations for roles
3. **Implement Role Assignment UI**: Admin panel for role management
4. **Add Audit Logging**: Track permission checks and role changes
5. **Implement Permission Caching**: Redis cache for frequently checked permissions
6. **Add Tests**: Unit and integration tests for RBAC
