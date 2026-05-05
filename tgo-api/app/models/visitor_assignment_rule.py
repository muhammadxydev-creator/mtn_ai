"""VisitorAssignmentRule model for MongoDB."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from beanie import Document
from pydantic import Field


class VisitorAssignmentRule(Document):
    """VisitorAssignmentRule model for visitor assignment rules in MongoDB."""

    project_id: UUID = Field(..., description="Associated project ID")
    name: str = Field(..., max_length=100, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    priority: int = Field(default=0, description="Rule priority (higher = more important)")
    is_active: bool = Field(default=True, description="Whether rule is active")
    conditions: dict = Field(default_factory=dict, description="Rule conditions")
    action: str = Field(..., max_length=50, description="Assignment action")
    staff_ids: List[UUID] = Field(default_factory=list, description="List of staff IDs to assign")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "api_visitor_assignment_rules"
        indexes = [
            [("project_id", 1)],
            [("is_active", 1)],
            [("priority", -1)],
            [("deleted_at", 1)],
        ]

    def is_deleted(self) -> bool:
        """Check if the rule is soft deleted."""
        return self.deleted_at is not None
