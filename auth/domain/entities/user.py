"""User domain entity."""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class User:

    id: Optional[str] = None
    email: str = ""
    hashed_password: str = ""
    full_name: str = ""
    is_active: bool = True
    is_verified: bool = False
    role_id: Optional[str] = None  # Reference to Role
    permissions: List[str] = field(default_factory=list)  # List of permission names
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

    def assign_role(self, role_id: str) -> None:
        """Assign a role to the user."""
        self.role_id = role_id
        self.updated_at = datetime.utcnow()

    def set_permissions(self, permissions: List[str]) -> None:
        """Set user permissions (typically loaded from role)."""
        self.permissions = permissions
        self.updated_at = datetime.utcnow()

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions

    def has_any_permission(self, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, permissions: List[str]) -> bool:
        """Check if user has all of the specified permissions."""
        return all(p in self.permissions for p in permissions)
