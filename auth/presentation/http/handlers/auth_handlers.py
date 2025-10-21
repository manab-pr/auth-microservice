"""Authentication HTTP handlers."""
from fastapi import APIRouter, Depends, HTTPException, status
from auth.presentation.http.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
    UpdateUserRequest,
    RefreshTokenRequest,
)
from auth.domain.usecases import (
    RegisterUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
    RefreshTokenUseCase,
)
from auth.presentation.http.dependencies import (
    get_register_use_case,
    get_login_use_case,
    get_logout_use_case,
    get_current_user_id,
    get_current_user_token,
    get_user_profile_use_case,
    get_update_user_profile_use_case,
    get_refresh_token_use_case,
)


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
):
    """
    Register a new user.

    Args:
        request: Registration request containing email, password, and full_name
        use_case: Injected registration use case

    Returns:
        UserResponse containing created user data

    Raises:
        HTTPException: If registration fails
    """
    try:
        user = await use_case.execute(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
        )

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
):
    """
    Login user and get access tokens.

    Args:
        request: Login request containing email and password
        use_case: Injected login use case

    Returns:
        TokenResponse containing access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    try:
        result = await use_case.execute(
            email=request.email,
            password=request.password,
        )

        return TokenResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type=result.token_type,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    token: str = Depends(get_current_user_token),
    use_case: LogoutUseCase = Depends(get_logout_use_case),
    current_user_id: str = Depends(get_current_user_id),
):
    """
    Logout user by revoking their access token.

    Args:
        token: The user's access token to revoke
        use_case: Injected logout use case
        current_user_id: ID of the authenticated user (from token)

    Returns:
        MessageResponse confirming logout

    Raises:
        HTTPException: If logout fails
    """
    try:
        await use_case.execute(access_token=token)
        return MessageResponse(message="Successfully logged out")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user_id: str = Depends(get_current_user_id),
    use_case: GetUserProfileUseCase = Depends(get_user_profile_use_case),
):
    """
    Get current authenticated user's profile.

    Args:
        current_user_id: ID of the authenticated user (from token)
        use_case: Injected get user profile use case

    Returns:
        UserResponse containing user data

    Raises:
        HTTPException: If user not found
    """
    try:
        user = await use_case.execute(user_id=current_user_id)

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile",
        )


@router.put("/me", response_model=UserResponse)
async def update_me(
    request: UpdateUserRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: UpdateUserProfileUseCase = Depends(get_update_user_profile_use_case),
):
    """
    Update current authenticated user's profile.

    Args:
        request: Update user request containing new data
        current_user_id: ID of the authenticated user (from token)
        use_case: Injected update user profile use case

    Returns:
        UserResponse containing updated user data

    Raises:
        HTTPException: If update fails
    """
    try:
        user = await use_case.execute(
            user_id=current_user_id, full_name=request.full_name
        )

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
):
    """
    Refresh access token using refresh token.

    Args:
        request: Refresh token request containing refresh token
        use_case: Injected refresh token use case

    Returns:
        TokenResponse containing new access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        result = await use_case.execute(refresh_token=request.refresh_token)

        return TokenResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type=result.token_type,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token",
        )
