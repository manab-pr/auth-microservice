"""List roles use case."""
from typing import List
from auth.domain.entities.role import Role
from auth.domain.ports.role_repository import RoleRepository


class ListRolesUseCase:
    """Use case for listing all roles."""

    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    async def execute(self) -> List[Role]:
        """
        List all roles in the system.

        Returns:
            List of all roles
        """
        return await self.role_repository.list_all()
