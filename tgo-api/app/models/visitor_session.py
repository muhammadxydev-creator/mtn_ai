"""VisitorSession model for MongoDB."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class SessionStatus(str, Enum):
    """Session status enumeration."""
    
    OPEN = "open"
    CLOSED = "closed"


class VisitorSession(Document):
    """VisitorSession model for tracking visitor sessions in MongoDB."""

    visitor_id: UUID = Field(..., description="Associated visitor ID")
    project_id: UUID = Field(..., description="Associated project ID")
    platform_id: UUID = Field(..., description="Associated platform ID")
    session_start: datetime = Field(default_factory=datetime.utcnow, description="Session start time")
    session_end: Optional[datetime] = Field(None, description="Session end time")
    is_active: bool = Field(default=True, description="Whether session is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "api_visitor_sessions"
        indexes = [
            [("visitor_id", 1)],
            [("project_id", 1)],
            [("platform_id", 1)],
            [("is_active", 1)],
            [("deleted_at", 1)],
        ]

    def is_deleted(self) -> bool:
        """Check if the session is soft deleted."""
        return self.deleted_at is not None
