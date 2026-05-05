"""ChannelMemoryClearance model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class ChannelMemoryClearance(Document):
    """ChannelMemoryClearance model for tracking channel memory clearance in MongoDB."""

    channel_id: UUID = Field(..., description="Associated channel ID")
    project_id: UUID = Field(..., description="Associated project ID")
    cleared_at: datetime = Field(default_factory=datetime.utcnow, description="Time when memory was cleared")
    cleared_by: Optional[UUID] = Field(None, description="Staff ID who cleared the memory")
    reason: Optional[str] = Field(None, description="Reason for clearing")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_channel_memory_clearances"
        indexes = [
            [("channel_id", 1)],
            [("project_id", 1)],
            [("cleared_at", -1)],
        ]
