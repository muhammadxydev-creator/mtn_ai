"""AIProvider model for MongoDB."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class AIProviderType(str, Enum):
    """AI Provider type enumeration."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    CUSTOM = "custom"


class AIProvider(Document):
    """AIProvider model for AI service providers in MongoDB."""

    project_id: UUID = Field(..., description="Associated project ID")
    name: str = Field(..., max_length=100, description="Provider name")
    provider_type: str = Field(..., max_length=50, description="Provider type")
    api_key: str = Field(..., max_length=500, description="API key for the provider")
    api_endpoint: Optional[str] = Field(None, max_length=500, description="Custom API endpoint")
    is_active: bool = Field(default=True, description="Whether provider is active")
    config: Optional[dict] = Field(default_factory=dict, description="Provider-specific configuration")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "api_ai_providers"
        indexes = [
            [("project_id", 1)],
            [("provider_type", 1)],
            [("is_active", 1)],
            [("deleted_at", 1)],
        ]

    def is_deleted(self) -> bool:
        """Check if the provider is soft deleted."""
        return self.deleted_at is not None
