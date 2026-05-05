"""StoreCredential model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class StoreCredential(Document):
    """StoreCredential model for storing third-party service credentials in MongoDB."""

    project_id: UUID = Field(..., description="Associated project ID")
    store_type: str = Field(..., max_length=50, description="Type of store (e.g., oauth, api_key)")
    store_name: str = Field(..., max_length=100, description="Name of the credential store")
    credential_data: dict = Field(default_factory=dict, description="Encrypted credential data")
    is_active: bool = Field(default=True, description="Whether credential is active")
    expires_at: Optional[datetime] = Field(None, description="Credential expiration time")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_store_credentials"
        indexes = [
            [("project_id", 1)],
            [("store_type", 1)],
            [("store_name", 1)],
        ]
