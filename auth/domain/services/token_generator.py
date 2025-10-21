"""Token generator service interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class TokenData:
    """Data extracted from a token."""

    user_id: str
    email: str
    jti: str  # JWT ID for revocation
    permissions: List[str] = field(default_factory=list)  # User permissions


class TokenGenerator(ABC):
    """Service interface for JWT token generation and validation."""

    @abstractmethod
    def generate_access_token(
        self, user_id: str, email: str, permissions: List[str] = None
    ) -> str:
        """
        Generate an access token for a user.

        Args:
            user_id: The user's ID
            email: The user's email
            permissions: List of user permissions

        Returns:
            The encoded JWT access token
        """
        pass

    @abstractmethod
    def generate_refresh_token(
        self, user_id: str, email: str, permissions: List[str] = None
    ) -> str:
        """
        Generate a refresh token for a user.

        Args:
            user_id: The user's ID
            email: The user's email
            permissions: List of user permissions

        Returns:
            The encoded JWT refresh token
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> TokenData:
        """
        Decode and validate a JWT token.

        Args:
            token: The JWT token to decode

        Returns:
            TokenData containing user information

        Raises:
            Exception if token is invalid or expired
        """
        pass

    @abstractmethod
    def get_token_expiry_seconds(self, is_refresh: bool = False) -> int:
        """
        Get the expiry time in seconds for a token.

        Args:
            is_refresh: Whether to get refresh token expiry (default: access token)

        Returns:
            Expiry time in seconds
        """
        pass
