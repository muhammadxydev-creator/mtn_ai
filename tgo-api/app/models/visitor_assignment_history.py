"""VisitorAssignmentHistory model for MongoDB."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class AssignmentSource(str, Enum):
    """Assignment source enumeration."""
    LLM = "llm"
    RULE = "rule"
    MANUAL = "manual"
    TRANSFER = "transfer"
    REJECT = "reject"
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCE = "load_balance"


class VisitorAssignmentHistory(Document):
    """VisitorAssignmentHistory model for tracking visitor assignment history in MongoDB."""

    visitor_id: UUID = Field(..., description="Associated visitor ID")
    project_id: UUID = Field(..., description="Associated project ID")
    staff_id: UUID = Field(..., description="Assigned staff ID")
    assigned_at: datetime = Field(default_factory=datetime.utcnow, description="Assignment time")
    unassigned_at: Optional[datetime] = Field(None, description="Unassignment time")
    reason: Optional[str] = Field(None, description="Reason for assignment/unassignment")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_visitor_assignment_histories"
        indexes = [
            [("visitor_id", 1)],
            [("project_id", 1)],
            [("staff_id", 1)],
            [("assigned_at", -1)],
        ]
