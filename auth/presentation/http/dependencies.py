"""FastAPI dependencies for dependency injection."""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.container import Container
from auth.domain.usecases import (
    RegisterUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
    RefreshTokenUseCase,
)

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
