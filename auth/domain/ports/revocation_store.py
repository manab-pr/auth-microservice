"""Revocation store port/interface for token blacklisting."""
from abc import ABC, abstractmethod
from typing import Optional


class RevocationStore(ABC):
    """Port/Interface for token revocation storage (blacklist)."""

    @abstractmethod
    async def revoke_token(self, token_jti: str, expires_in_seconds: int) -> None:
        """
        Revoke a token by adding it to the blacklist.

        Args:
            token_jti: The unique JWT ID (jti) of the token
            expires_in_seconds: How long to keep the token in blacklist
        """
        pass

    @abstractmethod
    async def is_token_revoked(self, token_jti: str) -> bool:
        """
        Check if a token is revoked.

        Args:
            token_jti: The unique JWT ID (jti) to check

        Returns:
            True if token is revoked, False otherwise
        """
        pass
