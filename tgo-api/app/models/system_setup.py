"""SystemSetup model for MongoDB."""

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class SystemSetup(Document):
    """SystemSetup model for system-wide configuration in MongoDB."""

    key: str = Field(..., max_length=100, unique=True, description="Configuration key")
    value: str = Field(..., description="Configuration value")
    description: Optional[str] = Field(None, description="Configuration description")
    is_public: bool = Field(default=False, description="Whether config is publicly accessible")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_system_setups"
        indexes = [
            [("key", 1)],
        ]
