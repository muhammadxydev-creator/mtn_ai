"""VisitorAIProfile model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class VisitorAIProfile(Document):
    """VisitorAIProfile model for storing AI-generated visitor profiles in MongoDB."""

    visitor_id: UUID = Field(..., description="Associated visitor ID", unique=True)
    project_id: UUID = Field(..., description="Associated project ID")
    profile_data: dict = Field(default_factory=dict, description="AI-generated profile data")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score of the profile")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_visitor_ai_profiles"
        indexes = [
            [("visitor_id", 1)],
            [("project_id", 1)],
        ]
