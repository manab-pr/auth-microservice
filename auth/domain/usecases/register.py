"""Register user use case."""
from auth.domain.entities import User
from auth.domain.ports import UserRepository
from auth.domain.services import PasswordHasher


class RegisterUserUseCase:
    """Use case for user registration."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(self, email: str, password: str, full_name: str) -> User:
        """
        Register a new user.

        Args:
            email: User's email address
            password: User's plain text password
            full_name: User's full name

        Returns:
            The created user

        Raises:
            ValueError: If user already exists or validation fails
        """
        # Validate email
        email = email.lower().strip()
        if not email:
            raise ValueError("Email is required")

        # Check if user already exists
        if await self.user_repository.exists_by_email(email):
            raise ValueError(f"User with email {email} already exists")

        # Validate password
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Hash password
        hashed_password = self.password_hasher.hash_password(password)

        # Create user entity
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_verified=False,
        )

        # Save to repository
        created_user = await self.user_repository.create(user)

        return created_user
