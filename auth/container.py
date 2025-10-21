"""Dependency injection container for auth module."""
from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as redis

from auth.domain.ports import UserRepository, RevocationStore
from auth.domain.services import PasswordHasher, TokenGenerator
from auth.domain.usecases import (
    RegisterUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
    RefreshTokenUseCase,
)
from auth.infra.mongodb import MongoUserRepository
from auth.infra.redis import RedisRevocationStore
from auth.infra.security import BcryptPasswordHasher, JWTTokenGenerator


class Container:
    """Dependency injection container for auth module."""

    def __init__(
        self,
        mongodb_database: AsyncIOMotorDatabase,
        redis_client: redis.Redis,
        jwt_secret_key: str,
        jwt_algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self._mongodb_database = mongodb_database
        self._redis_client = redis_client
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

        # Initialize singletons
        self._password_hasher = None
        self._token_generator = None
        self._user_repository = None
        self._revocation_store = None

    # Infrastructure layer
    def user_repository(self) -> UserRepository:
        """Get user repository instance."""
        if self._user_repository is None:
            self._user_repository = MongoUserRepository(self._mongodb_database)
        return self._user_repository

    def revocation_store(self) -> RevocationStore:
        """Get revocation store instance."""
        if self._revocation_store is None:
            self._revocation_store = RedisRevocationStore(self._redis_client)
        return self._revocation_store

    def password_hasher(self) -> PasswordHasher:
        """Get password hasher instance."""
        if self._password_hasher is None:
            self._password_hasher = BcryptPasswordHasher()
        return self._password_hasher

    def token_generator(self) -> TokenGenerator:
        """Get token generator instance."""
        if self._token_generator is None:
            self._token_generator = JWTTokenGenerator(
                secret_key=self._jwt_secret_key,
                algorithm=self._jwt_algorithm,
                access_token_expire_minutes=self._access_token_expire_minutes,
                refresh_token_expire_days=self._refresh_token_expire_days,
            )
        return self._token_generator

    # Use cases
    def register_use_case(self) -> RegisterUserUseCase:
        """Get register user use case."""
        return RegisterUserUseCase(
            user_repository=self.user_repository(),
            password_hasher=self.password_hasher(),
        )

    def login_use_case(self) -> LoginUseCase:
        """Get login use case."""
        return LoginUseCase(
            user_repository=self.user_repository(),
            password_hasher=self.password_hasher(),
            token_generator=self.token_generator(),
        )

    def logout_use_case(self) -> LogoutUseCase:
        """Get logout use case."""
        return LogoutUseCase(
            revocation_store=self.revocation_store(),
            token_generator=self.token_generator(),
        )

    def get_user_profile_use_case(self) -> GetUserProfileUseCase:
        """Get user profile use case."""
        return GetUserProfileUseCase(
            user_repository=self.user_repository(),
        )

    def update_user_profile_use_case(self) -> UpdateUserProfileUseCase:
        """Get update user profile use case."""
        return UpdateUserProfileUseCase(
            user_repository=self.user_repository(),
        )

    def refresh_token_use_case(self) -> RefreshTokenUseCase:
        """Get refresh token use case."""
        return RefreshTokenUseCase(
            user_repository=self.user_repository(),
            token_generator=self.token_generator(),
            revocation_store=self.revocation_store(),
        )
