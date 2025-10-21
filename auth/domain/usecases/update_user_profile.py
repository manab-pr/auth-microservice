"""Update user profile use case."""
from typing import Optional
from auth.domain.entities import User
from auth.domain.ports import UserRepository


class UpdateUserProfileUseCase:
    """Use case for updating user profile."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self, user_id: str, full_name: Optional[str] = None
    ) -> User:
        """
        Update user profile.

        Args:
            user_id: The user's ID
            full_name: New full name (optional)

        Returns:
            Updated user entity

        Raises:
            ValueError: If user not found or validation fails
        """
        # Get existing user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Update profile
        user.update_profile(full_name=full_name)

        # Save changes
        updated_user = await self.user_repository.update(user)

        return updated_user
