"""VisitorActivity model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class VisitorActivity(Document):
    """VisitorActivity model for tracking visitor activities in MongoDB."""

    visitor_id: UUID = Field(..., description="Associated visitor ID")
    project_id: UUID = Field(..., description="Associated project ID")
    activity_type: str = Field(..., max_length=50, description="Type of activity")
    activity_data: Optional[dict] = Field(default_factory=dict, description="Activity data payload")
    ip_address: Optional[str] = Field(None, max_length=45, description="Visitor IP address")
    user_agent: Optional[str] = Field(None, max_length=500, description="Browser user agent")
    page_url: Optional[str] = Field(None, max_length=2048, description="Page URL where activity occurred")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_visitor_activities"
        indexes = [
            [("visitor_id", 1)],
            [("project_id", 1)],
            [("activity_type", 1)],
            [("created_at", -1)],
        ]
