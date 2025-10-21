"""Role domain entity."""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class Role:
    """Role entity representing a collection of permissions."""

    id: Optional[str] = None
    name: str = ""  # e.g., "admin", "user", "super_admin"
    description: str = ""
    permission_ids: List[str] = field(default_factory=list)
    is_system: bool = False  # System roles cannot be deleted
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate role entity after initialization."""
        if self.name:
            self.name = self.name.lower().strip()

    def add_permission(self, permission_id: str) -> None:
        """Add a permission to this role."""
        if permission_id not in self.permission_ids:
            self.permission_ids.append(permission_id)
            self.updated_at = datetime.utcnow()

    def remove_permission(self, permission_id: str) -> None:
        """Remove a permission from this role."""
        if permission_id in self.permission_ids:
            self.permission_ids.remove(permission_id)
            self.updated_at = datetime.utcnow()

    def has_permission(self, permission_id: str) -> bool:
        """Check if this role has a specific permission."""
        return permission_id in self.permission_ids

    def update(
        self,
        description: Optional[str] = None,
        permission_ids: Optional[List[str]] = None,
    ) -> None:
        """Update role information."""
        if description is not None:
            self.description = description
        if permission_ids is not None:
            self.permission_ids = permission_ids
        self.updated_at = datetime.utcnow()
