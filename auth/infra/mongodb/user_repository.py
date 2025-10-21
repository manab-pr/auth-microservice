"""MongoDB implementation of user repository."""
from typing import Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth.domain.entities import User
from auth.domain.ports import UserRepository


class MongoUserRepository(UserRepository):
    """MongoDB implementation of user repository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database["users"]

    async def create(self, user: User) -> User:
        """Create a new user in MongoDB."""
        user_dict = {
            "email": user.email,
            "hashed_password": user.hashed_password,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

        result = await self.collection.insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID from MongoDB."""
        from bson import ObjectId

        try:
            user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return self._document_to_entity(user_doc)
            return None
        except Exception:
            return None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email from MongoDB."""
        user_doc = await self.collection.find_one({"email": email.lower()})
        if user_doc:
            return self._document_to_entity(user_doc)
        return None

    async def update(self, user: User) -> User:
        """Update existing user in MongoDB."""
        from bson import ObjectId

        user.updated_at = datetime.utcnow()

        update_dict = {
            "email": user.email,
            "hashed_password": user.hashed_password,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "updated_at": user.updated_at,
        }

        await self.collection.update_one(
            {"_id": ObjectId(user.id)}, {"$set": update_dict}
        )

        return user

    async def delete(self, user_id: str) -> bool:
        """Delete user by ID from MongoDB."""
        from bson import ObjectId

        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email in MongoDB."""
        count = await self.collection.count_documents({"email": email.lower()})
        return count > 0

    def _document_to_entity(self, doc: dict) -> User:
        """Convert MongoDB document to User entity."""
        return User(
            id=str(doc["_id"]),
            email=doc["email"],
            hashed_password=doc["hashed_password"],
            full_name=doc.get("full_name", ""),
            is_active=doc.get("is_active", True),
            is_verified=doc.get("is_verified", False),
            created_at=doc.get("created_at", datetime.utcnow()),
            updated_at=doc.get("updated_at", datetime.utcnow()),
        )
