"""Logout use case."""
from auth.domain.ports import RevocationStore
from auth.domain.services import TokenGenerator, TokenData


class LogoutUseCase:
    """Use case for user logout."""

    def __init__(
        self,
        revocation_store: RevocationStore,
        token_generator: TokenGenerator,
    ):
        self.revocation_store = revocation_store
        self.token_generator = token_generator

    async def execute(self, access_token: str) -> None:
        """
        Logout user by revoking their access token.

        Args:
            access_token: The user's access token to revoke

        Raises:
            Exception: If token is invalid
        """
        # Decode token to get JTI
        token_data = self.token_generator.decode_token(access_token)

        # Get token expiry time
        expiry_seconds = self.token_generator.get_token_expiry_seconds(is_refresh=False)

        # Revoke the token
        await self.revocation_store.revoke_token(
            token_jti=token_data.jti, expires_in_seconds=expiry_seconds
        )
