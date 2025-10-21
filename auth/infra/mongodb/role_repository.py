"""MongoDB implementation of Role repository."""
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth.domain.entities.role import Role
from auth.domain.ports.role_repository import RoleRepository


class MongoRoleRepository(RoleRepository):
    """MongoDB implementation of role repository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["roles"]

    async def create(self, role: Role) -> Role:
        """Create a new role."""
        role_dict = {
            "name": role.name,
            "description": role.description,
            "permission_ids": role.permission_ids,
            "is_system": role.is_system,
            "created_at": role.created_at,
            "updated_at": role.updated_at,
        }
        result = await self.collection.insert_one(role_dict)
        role.id = str(result.inserted_id)
        return role

    async def get_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        from bson import ObjectId

        try:
            doc = await self.collection.find_one({"_id": ObjectId(role_id)})
            if doc:
                return self._doc_to_role(doc)
            return None
        except Exception:
            return None

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        doc = await self.collection.find_one({"name": name})
        if doc:
            return self._doc_to_role(doc)
        return None

    async def list_all(self) -> List[Role]:
        """List all roles."""
        cursor = self.collection.find({})
        docs = await cursor.to_list(length=None)
        return [self._doc_to_role(doc) for doc in docs]

    async def update(self, role: Role) -> Role:
        """Update an existing role."""
        from bson import ObjectId
        from datetime import datetime

        role.updated_at = datetime.utcnow()
        update_dict = {
            "description": role.description,
            "permission_ids": role.permission_ids,
            "updated_at": role.updated_at,
        }
        await self.collection.update_one(
            {"_id": ObjectId(role.id)}, {"$set": update_dict}
        )
        return role

    async def delete(self, role_id: str) -> bool:
        """Delete a role."""
        from bson import ObjectId

        try:
            # Check if it's a system role
            doc = await self.collection.find_one({"_id": ObjectId(role_id)})
            if doc and doc.get("is_system", False):
                return False  # Cannot delete system roles

            result = await self.collection.delete_one({"_id": ObjectId(role_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def exists(self, name: str) -> bool:
        """Check if role exists by name."""
        count = await self.collection.count_documents({"name": name})
        return count > 0

    def _doc_to_role(self, doc: dict) -> Role:
        """Convert MongoDB document to Role entity."""
        return Role(
            id=str(doc["_id"]),
            name=doc.get("name", ""),
            description=doc.get("description", ""),
            permission_ids=doc.get("permission_ids", []),
            is_system=doc.get("is_system", False),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )
