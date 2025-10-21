"""Request password reset use case."""
import secrets
from datetime import datetime, timedelta
from auth.domain.entities import User
from auth.domain.ports import UserRepository


class RequestPasswordResetUseCase:
    """Use case for requesting password reset."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, email: str) -> str:
        """
        Request password reset for a user.

        Args:
            email: User's email address

        Returns:
            Reset token (in production, you'd send this via email)

        Raises:
            ValueError: If user not found
        """
        # Normalize email
        email = email.lower().strip()

        # Get user
        user = await self.user_repository.get_by_email(email)
        if not user:
            # For security, don't reveal if email exists or not
            # In production, you'd still return success but not send email
            raise ValueError("If the email exists, a reset link will be sent")

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)

        # In a real application, you would:
        # 1. Store the token with expiry in database/redis
        # 2. Send email with reset link containing the token
        # For this example, we'll just return the token

        return reset_token
