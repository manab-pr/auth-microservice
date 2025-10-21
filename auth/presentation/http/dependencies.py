"""FastAPI dependencies for dependency injection."""
from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.container import Container
from auth.domain.services import TokenData
from auth.domain.usecases import (
    RegisterUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
    RefreshTokenUseCase,
)
from auth.constants import ADMIN_ALL

# HTTP Bearer token scheme
security = HTTPBearer()

# Global container instance (will be initialized in main.py)
_container: Container = None


def set_container(container: Container):
    """Set the global container instance."""
    global _container
    _container = container


def get_container() -> Container:
    """Get the global container instance."""
    if _container is None:
        raise RuntimeError("Container not initialized. Call set_container() first.")
    return _container


# Use case dependencies
def get_register_use_case(
    container: Container = Depends(get_container),
) -> RegisterUserUseCase:
    """Get registration use case."""
    return container.register_use_case()


def get_login_use_case(
    container: Container = Depends(get_container),
) -> LoginUseCase:
    """Get login use case."""
    return container.login_use_case()


def get_logout_use_case(
    container: Container = Depends(get_container),
) -> LogoutUseCase:
    """Get logout use case."""
    return container.logout_use_case()


def get_user_profile_use_case(
    container: Container = Depends(get_container),
) -> GetUserProfileUseCase:
    """Get user profile use case."""
    return container.get_user_profile_use_case()


def get_update_user_profile_use_case(
    container: Container = Depends(get_container),
) -> UpdateUserProfileUseCase:
    """Get update user profile use case."""
    return container.update_user_profile_use_case()


def get_refresh_token_use_case(
    container: Container = Depends(get_container),
) -> RefreshTokenUseCase:
    """Get refresh token use case."""
    return container.refresh_token_use_case()


# Authentication dependencies
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    container: Container = Depends(get_container),
) -> str:
    """
    Get current authenticated user ID from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        container: Dependency injection container

    Returns:
        User ID extracted from token

    Raises:
        HTTPException: If token is invalid or revoked
    """
    token = credentials.credentials

    try:
        # Decode token
        token_generator = container.token_generator()
        token_data = token_generator.decode_token(token)

        # Check if token is revoked
        revocation_store = container.revocation_store()
        is_revoked = await revocation_store.is_token_revoked(token_data.jti)

        if is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token_data.user_id

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Get current user's access token.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        The access token string
    """
    return credentials.credentials


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    container: Container = Depends(get_container),
) -> TokenData:
    """
    Get current authenticated user's token data (including permissions).

    Args:
        credentials: HTTP Bearer token credentials
        container: Dependency injection container

    Returns:
        TokenData with user_id, email, jti, and permissions

    Raises:
        HTTPException: If token is invalid or revoked
    """
    token = credentials.credentials

    try:
        # Decode token
        token_generator = container.token_generator()
        token_data = token_generator.decode_token(token)

        # Check if token is revoked
        revocation_store = container.revocation_store()
        is_revoked = await revocation_store.is_token_revoked(token_data.jti)

        if is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token_data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permissions(*required_permissions: str):
    """
    Dependency factory to check if user has required permissions.

    Usage:
        @app.get("/admin/users")
        async def list_users(
            user: TokenData = Depends(require_permissions("users:list"))
        ):
            ...

    Args:
        *required_permissions: One or more permission strings required

    Returns:
        A dependency function that validates permissions
    """

    async def permission_checker(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        """Check if current user has required permissions."""
        # Super admin has all permissions
        if ADMIN_ALL in current_user.permissions:
            return current_user

        # Check if user has all required permissions
        missing_permissions = [
            perm
            for perm in required_permissions
            if perm not in current_user.permissions
        ]

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing_permissions)}",
            )

        return current_user

    return permission_checker


def require_any_permission(*required_permissions: str):
    """
    Dependency factory to check if user has ANY of the required permissions.

    Usage:
        @app.get("/content")
        async def view_content(
            user: TokenData = Depends(require_any_permission("content:read", "content:admin"))
        ):
            ...

    Args:
        *required_permissions: One or more permission strings (user needs at least one)

    Returns:
        A dependency function that validates permissions
    """

    async def permission_checker(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        """Check if current user has any of the required permissions."""
        # Super admin has all permissions
        if ADMIN_ALL in current_user.permissions:
            return current_user

        # Check if user has at least one of the required permissions
        has_permission = any(
            perm in current_user.permissions for perm in required_permissions
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(required_permissions)}",
            )

        return current_user

    return permission_checker
