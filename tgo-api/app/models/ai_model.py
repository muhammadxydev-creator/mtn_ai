"""AIModel model for MongoDB."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class AIModelType(str, Enum):
    """AI Model type enumeration."""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE = "image"
    AUDIO = "audio"


class AIModel(Document):
    """AIModel model for AI models in MongoDB."""

    provider_id: UUID = Field(..., description="Associated AI provider ID")
    project_id: UUID = Field(..., description="Associated project ID")
    name: str = Field(..., max_length=200, description="Model name")
    model_type: str = Field(default=AIModelType.CHAT.value, max_length=50, description="Model type")
    is_active: bool = Field(default=True, description="Whether model is active")
    config: Optional[dict] = Field(default_factory=dict, description="Model-specific configuration")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "api_ai_models"
        indexes = [
            [("provider_id", 1)],
            [("project_id", 1)],
            [("model_type", 1)],
            [("is_active", 1)],
            [("deleted_at", 1)],
        ]

    def is_deleted(self) -> bool:
        """Check if the model is soft deleted."""
        return self.deleted_at is not None
