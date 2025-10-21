"""Permission domain entity."""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Permission:
    """Permission entity representing an action that can be performed."""

    id: Optional[str] = None
    name: str = ""  # e.g., "users:create", "orders:read"
    description: str = ""
    resource: str = ""  # e.g., "users", "orders", "quotes"
    action: str = ""  # e.g., "create", "read", "update", "delete"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate permission entity after initialization."""
        if self.name:
            self.name = self.name.lower().strip()
        if self.resource:
            self.resource = self.resource.lower().strip()
        if self.action:
            self.action = self.action.lower().strip()

    def update(self, description: Optional[str] = None) -> None:
        """Update permission information."""
        if description is not None:
            self.description = description
        self.updated_at = datetime.utcnow()

    def matches(self, resource: str, action: str) -> bool:
        """Check if this permission matches the given resource and action."""
        return self.resource == resource and self.action == action

    @staticmethod
    def create_name(resource: str, action: str) -> str:
        """Create a permission name from resource and action."""
        return f"{resource}:{action}"
