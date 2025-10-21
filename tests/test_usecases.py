"""Unit tests for use cases."""
import pytest
from auth.domain.usecases import (
    RegisterUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
)
from auth.domain.entities import User


class TestRegisterUserUseCase:
    """Tests for RegisterUserUseCase."""

    @pytest.mark.asyncio
    async def test_register_new_user_success(
        self, mock_user_repository, mock_password_hasher
    ):
        """Test successful user registration."""
        # Arrange
        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.create.return_value = User(
            id="123",
            email="newuser@example.com",
            hashed_password="hashed_password",
            full_name="New User",
            is_active=True,
            is_verified=False,
        )

        use_case = RegisterUserUseCase(mock_user_repository, mock_password_hasher)

        # Act
        result = await use_case.execute(
            email="newuser@example.com",
            password="password123",
            full_name="New User",
        )

        # Assert
        assert result.email == "newuser@example.com"
        assert result.full_name == "New User"
        mock_user_repository.exists_by_email.assert_called_once()
        mock_password_hasher.hash_password.assert_called_once_with("password123")
        mock_user_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_existing_user_fails(
        self, mock_user_repository, mock_password_hasher
    ):
        """Test registration fails for existing user."""
        # Arrange
        mock_user_repository.exists_by_email.return_value = True

        use_case = RegisterUserUseCase(mock_user_repository, mock_password_hasher)

        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            await use_case.execute(
                email="existing@example.com",
                password="password123",
                full_name="Existing User",
            )

    @pytest.mark.asyncio
    async def test_register_short_password_fails(
        self, mock_user_repository, mock_password_hasher
    ):
        """Test registration fails with short password."""
        # Arrange
        mock_user_repository.exists_by_email.return_value = False

        use_case = RegisterUserUseCase(mock_user_repository, mock_password_hasher)

        # Act & Assert
        with pytest.raises(ValueError, match="at least 8 characters"):
            await use_case.execute(
                email="user@example.com", password="short", full_name="User"
            )


class TestLoginUseCase:
    """Tests for LoginUseCase."""

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        mock_user,
        mock_user_repository,
        mock_password_hasher,
        mock_token_generator,
    ):
        """Test successful login."""
        # Arrange
        mock_user_repository.get_by_email.return_value = mock_user
        mock_password_hasher.verify_password.return_value = True

        use_case = LoginUseCase(
            mock_user_repository, mock_password_hasher, mock_token_generator
        )

        # Act
        result = await use_case.execute(
            email="test@example.com", password="password123"
        )

        # Assert
        assert result.access_token == "access_token_123"
        assert result.refresh_token == "refresh_token_123"
        assert result.token_type == "bearer"
        mock_user_repository.get_by_email.assert_called_once_with("test@example.com")
        mock_password_hasher.verify_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(
        self,
        mock_user,
        mock_user_repository,
        mock_password_hasher,
        mock_token_generator,
    ):
        """Test login with invalid credentials."""
        # Arrange
        mock_user_repository.get_by_email.return_value = mock_user
        mock_password_hasher.verify_password.return_value = False

        use_case = LoginUseCase(
            mock_user_repository, mock_password_hasher, mock_token_generator
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email or password"):
            await use_case.execute(
                email="test@example.com", password="wrongpassword"
            )

    @pytest.mark.asyncio
    async def test_login_user_not_found(
        self, mock_user_repository, mock_password_hasher, mock_token_generator
    ):
        """Test login with non-existent user."""
        # Arrange
        mock_user_repository.get_by_email.return_value = None

        use_case = LoginUseCase(
            mock_user_repository, mock_password_hasher, mock_token_generator
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email or password"):
            await use_case.execute(
                email="nonexistent@example.com", password="password123"
            )


class TestGetUserProfileUseCase:
    """Tests for GetUserProfileUseCase."""

    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, mock_user, mock_user_repository):
        """Test successful user profile retrieval."""
        # Arrange
        mock_user_repository.get_by_id.return_value = mock_user

        use_case = GetUserProfileUseCase(mock_user_repository)

        # Act
        result = await use_case.execute(user_id="123")

        # Assert
        assert result.id == "123"
        assert result.email == "test@example.com"
        mock_user_repository.get_by_id.assert_called_once_with("123")

    @pytest.mark.asyncio
    async def test_get_user_profile_not_found(self, mock_user_repository):
        """Test get user profile when user not found."""
        # Arrange
        mock_user_repository.get_by_id.return_value = None

        use_case = GetUserProfileUseCase(mock_user_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            await use_case.execute(user_id="nonexistent")


class TestUpdateUserProfileUseCase:
    """Tests for UpdateUserProfileUseCase."""

    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, mock_user, mock_user_repository):
        """Test successful user profile update."""
        # Arrange
        mock_user_repository.get_by_id.return_value = mock_user
        mock_user_repository.update.return_value = mock_user

        use_case = UpdateUserProfileUseCase(mock_user_repository)

        # Act
        result = await use_case.execute(user_id="123", full_name="Updated Name")

        # Assert
        assert result.full_name == "Updated Name"
        mock_user_repository.get_by_id.assert_called_once_with("123")
        mock_user_repository.update.assert_called_once()
