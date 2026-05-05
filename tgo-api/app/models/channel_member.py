"""ChannelMember model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class ChannelMember(Document):
    """ChannelMember model for chat channel members in MongoDB."""

    channel_id: UUID = Field(..., description="Associated channel ID")
    project_id: UUID = Field(..., description="Associated project ID")
    member_type: str = Field(..., max_length=20, description="Member type (staff, visitor, ai)")
    member_id: UUID = Field(..., description="Member ID (staff or visitor)")
    role: str = Field(default="member", max_length=50, description="Role in channel")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = Field(None, description="Time when member left")
    is_active: bool = Field(default=True, description="Whether member is active in channel")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_channel_members"
        indexes = [
            [("channel_id", 1)],
            [("project_id", 1)],
            [("member_id", 1)],
            [("is_active", 1)],
        ]
