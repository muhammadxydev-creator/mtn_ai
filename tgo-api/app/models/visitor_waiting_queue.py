"""VisitorWaitingQueue model for MongoDB."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class WaitingStatus(str, Enum):
    """Waiting status enumeration."""
    WAITING = "waiting"
    ASSIGNED = "assigned"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class QueueSource(str, Enum):
    """Queue source enumeration."""
    NO_STAFF = "no_staff"
    AI_REJECT = "ai_reject"
    MANUAL = "manual"
    TRANSFER = "transfer"


class VisitorWaitingQueue(Document):
    """VisitorWaitingQueue model for managing visitor waiting queue in MongoDB."""

    visitor_id: UUID = Field(..., description="Associated visitor ID", unique=True)
    project_id: UUID = Field(..., description="Associated project ID")
    queued_at: datetime = Field(default_factory=datetime.utcnow, description="Time when visitor was queued")
    position: int = Field(default=0, description="Position in the waiting queue")
    estimated_wait_time: Optional[int] = Field(None, description="Estimated wait time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_visitor_waiting_queues"
        indexes = [
            [("visitor_id", 1)],
            [("project_id", 1)],
            [("queued_at", 1)],
        ]
