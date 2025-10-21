"""Assign role to user use case."""
from auth.domain.ports import UserRepository, RoleRepository, PermissionRepository


class AssignRoleUseCase:
    """Use case for assigning a role to a user."""

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.permission_repository = permission_repository

    async def execute(self, user_id: str, role_id: str) -> None:
        """
        Assign a role to a user and load their permissions.

        Args:
            user_id: The user's ID
            role_id: The role's ID to assign

        Raises:
            ValueError: If user or role not found
        """
        # Get user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Get role
        role = await self.role_repository.get_by_id(role_id)
        if not role:
            raise ValueError("Role not found")

        # Assign role to user
        user.assign_role(role_id)

        # Load permissions for the role
        permissions = await self.permission_repository.get_by_ids(role.permission_ids)
        permission_names = [perm.name for perm in permissions]

        # Set user permissions
        user.set_permissions(permission_names)

        # Update user in repository
        await self.user_repository.update(user)
