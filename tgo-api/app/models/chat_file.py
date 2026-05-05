"""ChatFile model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class ChatFile(Document):
    """ChatFile model for files shared in chat channels in MongoDB."""

    channel_id: UUID = Field(..., description="Associated channel ID")
    project_id: UUID = Field(..., description="Associated project ID")
    file_name: str = Field(..., max_length=255, description="Original file name")
    file_path: str = Field(..., max_length=512, description="Storage path of the file")
    file_size: int = Field(default=0, description="File size in bytes")
    file_type: str = Field(..., max_length=100, description="MIME type of the file")
    uploaded_by: UUID = Field(..., description="User ID who uploaded the file")
    message_id: Optional[UUID] = Field(None, description="Associated message ID if any")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "api_chat_files"
        indexes = [
            [("channel_id", 1)],
            [("project_id", 1)],
            [("uploaded_by", 1)],
            [("deleted_at", 1)],
        ]

    def is_deleted(self) -> bool:
        """Check if the file is soft deleted."""
        return self.deleted_at is not None
