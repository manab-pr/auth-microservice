"""User domain entity."""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class User:

    id: Optional[str] = None
    email: str = ""
    hashed_password: str = ""
    full_name: str = ""
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate user entity after initialization."""
        if self.email:
            self.email = self.email.lower().strip()

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def verify(self) -> None:
        """Mark user as verified."""
        self.is_verified = True
        self.updated_at = datetime.utcnow()

    def update_password(self, hashed_password: str) -> None:
        """Update user password with hashed password."""
        self.hashed_password = hashed_password
        self.updated_at = datetime.utcnow()

    def update_profile(self, full_name: Optional[str] = None) -> None:
        """Update user profile information."""
        if full_name is not None:
            self.full_name = full_name
        self.updated_at = datetime.utcnow()
