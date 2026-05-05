"""Project model for MongoDB."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import Field


class Project(Document):
    """Project model for multi-tenant isolation in MongoDB."""

    name: str = Field(..., description="Project name")
    api_key: str = Field(..., description="API key for authentication")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "projects"
        indexes = [
            [("api_key", 1)],
            [("deleted_at", 1)],
            [("created_at", -1)],
        ]

    def is_deleted(self) -> bool:
        """Check if the project is soft deleted."""
        return self.deleted_at is not None
