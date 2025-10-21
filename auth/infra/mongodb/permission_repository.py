"""MongoDB implementation of Permission repository."""
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth.domain.entities.permission import Permission
from auth.domain.ports.permission_repository import PermissionRepository


class MongoPermissionRepository(PermissionRepository):
    """MongoDB implementation of permission repository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["permissions"]

    async def create(self, permission: Permission) -> Permission:
        """Create a new permission."""
        permission_dict = {
            "name": permission.name,
            "description": permission.description,
            "resource": permission.resource,
            "action": permission.action,
            "created_at": permission.created_at,
            "updated_at": permission.updated_at,
        }
        result = await self.collection.insert_one(permission_dict)
        permission.id = str(result.inserted_id)
        return permission

    async def get_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        from bson import ObjectId

        try:
            doc = await self.collection.find_one({"_id": ObjectId(permission_id)})
            if doc:
                return self._doc_to_permission(doc)
            return None
        except Exception:
            return None

    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        doc = await self.collection.find_one({"name": name})
        if doc:
            return self._doc_to_permission(doc)
        return None

    async def get_by_ids(self, permission_ids: List[str]) -> List[Permission]:
        """Get multiple permissions by their IDs."""
        from bson import ObjectId

        try:
            object_ids = [ObjectId(pid) for pid in permission_ids]
            cursor = self.collection.find({"_id": {"$in": object_ids}})
            docs = await cursor.to_list(length=None)
            return [self._doc_to_permission(doc) for doc in docs]
        except Exception:
            return []

    async def list_all(self) -> List[Permission]:
        """List all permissions."""
        cursor = self.collection.find({})
        docs = await cursor.to_list(length=None)
        return [self._doc_to_permission(doc) for doc in docs]

    async def update(self, permission: Permission) -> Permission:
        """Update an existing permission."""
        from bson import ObjectId
        from datetime import datetime

        permission.updated_at = datetime.utcnow()
        update_dict = {
            "description": permission.description,
            "resource": permission.resource,
            "action": permission.action,
            "updated_at": permission.updated_at,
        }
        await self.collection.update_one(
            {"_id": ObjectId(permission.id)}, {"$set": update_dict}
        )
        return permission

    async def delete(self, permission_id: str) -> bool:
        """Delete a permission."""
        from bson import ObjectId

        try:
            result = await self.collection.delete_one({"_id": ObjectId(permission_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def exists(self, name: str) -> bool:
        """Check if permission exists by name."""
        count = await self.collection.count_documents({"name": name})
        return count > 0

    def _doc_to_permission(self, doc: dict) -> Permission:
        """Convert MongoDB document to Permission entity."""
        return Permission(
            id=str(doc["_id"]),
            name=doc.get("name", ""),
            description=doc.get("description", ""),
            resource=doc.get("resource", ""),
            action=doc.get("action", ""),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )
