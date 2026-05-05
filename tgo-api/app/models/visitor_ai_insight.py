"""VisitorAIInsight model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class VisitorAIInsight(Document):
    """VisitorAIInsight model for storing AI-generated visitor insights in MongoDB."""

    visitor_id: UUID = Field(..., description="Associated visitor ID")
    project_id: UUID = Field(..., description="Associated project ID")
    insight_type: str = Field(..., max_length=50, description="Type of insight")
    insight_data: dict = Field(default_factory=dict, description="AI-generated insight data")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_visitor_ai_insights"
        indexes = [
            [("visitor_id", 1)],
            [("project_id", 1)],
            [("insight_type", 1)],
            [("created_at", -1)],
        ]
