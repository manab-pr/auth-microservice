"""Bcrypt implementation of password hasher."""
from passlib.context import CryptContext
from auth.domain.services import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    """Bcrypt implementation of password hashing."""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password using bcrypt."""
        return self.pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a bcrypt hashed password."""
        return self.pwd_context.verify(plain_password, hashed_password)
