"""Reset password use case."""
from auth.domain.entities import User
from auth.domain.ports import UserRepository
from auth.domain.services import PasswordHasher


class ResetPasswordUseCase:
    """Use case for resetting password."""

    def __init__(
        self, user_repository: UserRepository, password_hasher: PasswordHasher
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(self, email: str, new_password: str) -> None:
        """
        Reset user password.

        Args:
            email: User's email
            new_password: New password

        Raises:
            ValueError: If validation fails
        """
        # Validate password
        if not new_password or len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Get user
        user = await self.user_repository.get_by_email(email.lower())
        if not user:
            raise ValueError("User not found")

        # Hash new password
        hashed_password = self.password_hasher.hash_password(new_password)

        # Update password
        user.update_password(hashed_password)

        # Save user
        await self.user_repository.update(user)
