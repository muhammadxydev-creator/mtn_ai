"""VisitorTag model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class VisitorTag(Document):
    """VisitorTag model for associating visitors with tags in MongoDB."""

    visitor_id: UUID = Field(..., description="Associated visitor ID")
    tag_id: str = Field(..., max_length=255, description="Associated tag ID (Base64 encoded)")
    project_id: UUID = Field(..., description="Associated project ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "api_visitor_tags"
        indexes = [
            [("visitor_id", 1)],
            [("tag_id", 1)],
            [("project_id", 1)],
            [("deleted_at", 1)],
        ]

    def is_deleted(self) -> bool:
        """Check if the visitor tag is soft deleted."""
        return self.deleted_at is not None
