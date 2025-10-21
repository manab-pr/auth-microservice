"""Login use case."""
from dataclasses import dataclass
from auth.domain.ports import UserRepository
from auth.domain.services import PasswordHasher, TokenGenerator


@dataclass
class LoginResult:
    """Result of login operation."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginUseCase:
    """Use case for user login."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_generator: TokenGenerator,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_generator = token_generator

    async def execute(self, email: str, password: str) -> LoginResult:
        """
        Authenticate user and generate tokens.

        Args:
            email: User's email address
            password: User's plain text password

        Returns:
            LoginResult containing access and refresh tokens

        Raises:
            ValueError: If credentials are invalid
        """
        # Normalize email
        email = email.lower().strip()

        # Get user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not self.password_hasher.verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is deactivated")

        # Generate tokens with user permissions
        access_token = self.token_generator.generate_access_token(
            user_id=user.id, email=user.email, permissions=user.permissions
        )
        refresh_token = self.token_generator.generate_refresh_token(
            user_id=user.id, email=user.email, permissions=user.permissions
        )

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
        )
