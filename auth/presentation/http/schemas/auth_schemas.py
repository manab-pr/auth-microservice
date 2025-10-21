"""Authentication schemas/DTOs for HTTP requests and responses."""
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1)


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class UpdateUserRequest(BaseModel):
    """Request schema for updating user profile."""

    full_name: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token."""

    refresh_token: str
