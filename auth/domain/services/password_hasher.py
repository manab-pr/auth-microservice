"""Password hasher service interface."""
from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Service interface for password hashing operations."""

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """
        Hash a plain text password.

        Args:
            plain_password: The plain text password

        Returns:
            The hashed password
        """
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.

        Args:
            plain_password: The plain text password
            hashed_password: The hashed password to verify against

        Returns:
            True if password matches, False otherwise
        """
        pass
