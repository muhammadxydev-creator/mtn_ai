"""Tag model for MongoDB."""

import base64
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class TagCategory(str, Enum):
    """Tag category enumeration."""

    VISITOR = "visitor"
    KNOWLEDGE = "knowledge"


class Tag(Document):
    """Tag model for categorization and labeling system in MongoDB."""

    name: str = Field(..., max_length=50, description="Tag name (English)")
    name_zh: Optional[str] = Field(None, max_length=50, description="Tag name in Chinese")
    project_id: UUID = Field(..., description="Associated project ID")
    category: str = Field(..., max_length=20, description="Tag category: visitor or knowledge")
    weight: int = Field(default=0, ge=0, le=10, description="Tag importance/priority weight")
    color: Optional[str] = Field(None, max_length=20, description="Tag color")
    description: Optional[str] = Field(None, max_length=255, description="Tag description")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "api_tags"
        indexes = [
            [("project_id", 1)],
            [("category", 1)],
            [("deleted_at", 1)],
            [("project_id", 1), ("name", 1)],
        ]

    def __init__(self, **data):
        if "id" not in data and "name" in data and "category" in data:
            data["id"] = self.generate_id(data["name"], data["category"])
        super().__init__(**data)

    def is_deleted(self) -> bool:
        """Check if the tag is soft deleted."""
        return self.deleted_at is not None

    @classmethod
    def generate_id(cls, name: str, category: TagCategory) -> str:
        """Generate Base64 encoded ID for a tag."""
        id_string = f"{name}@{category.value}"
        return base64.b64encode(id_string.encode()).decode()

    @classmethod
    def decode_id(cls, tag_id: str) -> tuple[str, str]:
        """Decode Base64 tag ID to get name and category."""
        try:
            decoded = base64.b64decode(tag_id.encode()).decode()
            name, category = decoded.split("@", 1)
            return name, category
        except Exception:
            raise ValueError(f"Invalid tag ID format: {tag_id}")
