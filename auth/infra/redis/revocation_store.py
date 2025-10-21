"""Redis implementation of revocation store."""
from typing import Optional
import redis.asyncio as redis
from auth.domain.ports import RevocationStore


class RedisRevocationStore(RevocationStore):
    """Redis implementation of token revocation store."""

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.key_prefix = "revoked_token:"

    async def revoke_token(self, token_jti: str, expires_in_seconds: int) -> None:
        """Revoke a token by adding it to Redis with expiry."""
        key = f"{self.key_prefix}{token_jti}"
        await self.redis_client.setex(key, expires_in_seconds, "revoked")

    async def is_token_revoked(self, token_jti: str) -> bool:
        """Check if a token is revoked in Redis."""
        key = f"{self.key_prefix}{token_jti}"
        result = await self.redis_client.get(key)
        return result is not None
