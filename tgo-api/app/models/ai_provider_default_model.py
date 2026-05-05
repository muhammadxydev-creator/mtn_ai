"""AIProviderDefaultModel model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class AIProviderDefaultModel(Document):
    """AIProviderDefaultModel model for storing default model settings per provider in MongoDB."""

    project_id: UUID = Field(..., description="Associated project ID")
    provider_id: UUID = Field(..., description="Associated AI provider ID")
    model_id: UUID = Field(..., description="Default AI model ID")
    model_type: str = Field(..., max_length=50, description="Model type (chat, completion, etc.)")
    is_active: bool = Field(default=True, description="Whether this default is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_ai_provider_default_models"
        indexes = [
            [("project_id", 1)],
            [("provider_id", 1)],
            [("model_type", 1)],
        ]
