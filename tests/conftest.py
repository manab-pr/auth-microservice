"""Pytest configuration and fixtures."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from auth.domain.entities import User
from auth.domain.ports import UserRepository, RevocationStore
from auth.domain.services import PasswordHasher, TokenGenerator, TokenData


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return User(
        id="123",
        email="test@example.com",
        hashed_password="hashed_password_123",
        full_name="Test User",
        is_active=True,
        is_verified=False,
    )


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    repository = AsyncMock(spec=UserRepository)
    return repository


@pytest.fixture
def mock_password_hasher():
    """Create a mock password hasher."""
    hasher = MagicMock(spec=PasswordHasher)
    hasher.hash_password.return_value = "hashed_password"
    hasher.verify_password.return_value = True
    return hasher


@pytest.fixture
def mock_token_generator():
    """Create a mock token generator."""
    generator = MagicMock(spec=TokenGenerator)
    generator.generate_access_token.return_value = "access_token_123"
    generator.generate_refresh_token.return_value = "refresh_token_123"
    generator.decode_token.return_value = TokenData(
        user_id="123", email="test@example.com", jti="jti_123"
    )
    generator.get_token_expiry_seconds.return_value = 1800
    return generator


@pytest.fixture
def mock_revocation_store():
    """Create a mock revocation store."""
    store = AsyncMock(spec=RevocationStore)
    store.is_token_revoked.return_value = False
    return store
