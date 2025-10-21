"""Role repository port (interface)."""
from abc import ABC, abstractmethod
from typing import List, Optional
from auth.domain.entities.role import Role


class RoleRepository(ABC):
    """Abstract role repository interface."""

    @abstractmethod
    async def create(self, role: Role) -> Role:
        """Create a new role."""
        pass

    @abstractmethod
    async def get_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        pass

    @abstractmethod
    async def list_all(self) -> List[Role]:
        """List all roles."""
        pass

    @abstractmethod
    async def update(self, role: Role) -> Role:
        """Update an existing role."""
        pass

    @abstractmethod
    async def delete(self, role_id: str) -> bool:
        """Delete a role."""
        pass

    @abstractmethod
    async def exists(self, name: str) -> bool:
        """Check if role exists by name."""
        pass
