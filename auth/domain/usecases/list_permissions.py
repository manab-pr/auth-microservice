"""List permissions use case."""
from typing import List
from auth.domain.entities.permission import Permission
from auth.domain.ports.permission_repository import PermissionRepository


class ListPermissionsUseCase:
    """Use case for listing all permissions."""

    def __init__(self, permission_repository: PermissionRepository):
        self.permission_repository = permission_repository

    async def execute(self) -> List[Permission]:
        """
        List all permissions in the system.

        Returns:
            List of all permissions
        """
        return await self.permission_repository.list_all()
