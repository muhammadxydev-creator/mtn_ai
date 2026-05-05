"""ProjectAIConfig model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class ProjectAIConfig(Document):
    """ProjectAIConfig model for project-specific AI configuration in MongoDB."""

    project_id: UUID = Field(..., description="Associated project ID", unique=True)
    default_provider_id: Optional[UUID] = Field(None, description="Default AI provider ID")
    default_model_id: Optional[UUID] = Field(None, description="Default AI model ID")
    ai_enabled: bool = Field(default=True, description="Whether AI is enabled for this project")
    config: dict = Field(default_factory=dict, description="Additional AI configuration")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_project_ai_configs"
        indexes = [
            [("project_id", 1)],
        ]
