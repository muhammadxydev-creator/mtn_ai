"""ProjectOnboardingProgress model for MongoDB."""

from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

from beanie import Document
from pydantic import Field


class ProjectOnboardingProgress(Document):
    """ProjectOnboardingProgress model for tracking project onboarding progress in MongoDB."""

    project_id: UUID = Field(..., description="Associated project ID", unique=True)
    current_step: str = Field(default="start", max_length=50, description="Current onboarding step")
    completed_steps: Dict[str, datetime] = Field(default_factory=dict, description="Completed steps with completion time")
    is_completed: bool = Field(default=False, description="Whether onboarding is complete")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_project_onboarding_progress"
        indexes = [
            [("project_id", 1)],
        ]
