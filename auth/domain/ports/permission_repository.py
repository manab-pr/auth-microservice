"""Permission repository port (interface)."""
from abc import ABC, abstractmethod
from typing import List, Optional
from auth.domain.entities.permission import Permission


class PermissionRepository(ABC):
    """Abstract permission repository interface."""

    @abstractmethod
    async def create(self, permission: Permission) -> Permission:
        """Create a new permission."""
        pass

    @abstractmethod
    async def get_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        pass

    @abstractmethod
    async def get_by_ids(self, permission_ids: List[str]) -> List[Permission]:
        """Get multiple permissions by their IDs."""
        pass

    @abstractmethod
    async def list_all(self) -> List[Permission]:
        """List all permissions."""
        pass

    @abstractmethod
    async def update(self, permission: Permission) -> Permission:
        """Update an existing permission."""
        pass

    @abstractmethod
    async def delete(self, permission_id: str) -> bool:
        """Delete a permission."""
        pass

    @abstractmethod
    async def exists(self, name: str) -> bool:
        """Check if permission exists by name."""
        pass
