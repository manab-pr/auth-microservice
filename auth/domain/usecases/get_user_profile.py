"""Get user profile use case."""
from typing import Optional
from auth.domain.entities import User
from auth.domain.ports import UserRepository


class GetUserProfileUseCase:
    """Use case for getting user profile."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: str) -> User:
        """
        Get user profile by user ID.

        Args:
            user_id: The user's ID

        Returns:
            User entity

        Raises:
            ValueError: If user not found
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return user
