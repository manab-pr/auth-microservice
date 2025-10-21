"""Refresh token use case."""
from dataclasses import dataclass
from auth.domain.ports import UserRepository, RevocationStore
from auth.domain.services import TokenGenerator


@dataclass
class RefreshTokenResult:
    """Result of refresh token operation."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenUseCase:
    """Use case for refreshing access token."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_generator: TokenGenerator,
        revocation_store: RevocationStore,
    ):
        self.user_repository = user_repository
        self.token_generator = token_generator
        self.revocation_store = revocation_store

    async def execute(self, refresh_token: str) -> RefreshTokenResult:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            RefreshTokenResult containing new access and refresh tokens

        Raises:
            ValueError: If refresh token is invalid or user not found
        """
        # Decode refresh token
        try:
            token_data = self.token_generator.decode_token(refresh_token)
        except Exception as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")

        # Check if token is revoked
        is_revoked = await self.revocation_store.is_token_revoked(token_data.jti)
        if is_revoked:
            raise ValueError("Refresh token has been revoked")

        # Get user
        user = await self.user_repository.get_by_id(token_data.user_id)
        if not user:
            raise ValueError("User not found")

        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is deactivated")

        # Revoke old refresh token
        expiry_seconds = self.token_generator.get_token_expiry_seconds(is_refresh=True)
        await self.revocation_store.revoke_token(token_data.jti, expiry_seconds)

        # Generate new tokens
        new_access_token = self.token_generator.generate_access_token(
            user_id=user.id, email=user.email
        )
        new_refresh_token = self.token_generator.generate_refresh_token(
            user_id=user.id, email=user.email
        )

        return RefreshTokenResult(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
