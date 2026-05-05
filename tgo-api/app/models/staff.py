"""Staff model for MongoDB."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class StaffRole(str, Enum):
    """Staff role enumeration."""

    USER = "user"
    ADMIN = "admin"
    AGENT = "agent"


class StaffStatus(str, Enum):
    """Staff status enumeration."""

    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


class Staff(Document):
    """Staff model for human users and AI agents in MongoDB."""

    project_id: UUID = Field(..., description="Associated project ID")
    username: str = Field(..., max_length=50, description="Staff username for login")
    password_hash: str = Field(..., max_length=255, description="Hashed password")
    name: Optional[str] = Field(None, max_length=100, description="Staff real name")
    nickname: Optional[str] = Field(None, max_length=100, description="Staff display name")
    avatar_url: Optional[str] = Field(None, max_length=255, description="Staff avatar URL")
    description: Optional[str] = Field(None, max_length=500, description="Staff description for LLM assignment")
    role: str = Field(default=StaffRole.USER.value, max_length=20, description="Staff role")
    status: str = Field(default=StaffStatus.OFFLINE.value, max_length=20, description="Staff status")
    is_active: bool = Field(default=True, description="Whether staff is active for service")
    service_paused: bool = Field(default=False, description="Whether staff paused accepting new visitors")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "api_staff"
        indexes = [
            [("project_id", 1)],
            [("username", 1)],
            [("role", 1)],
            [("status", 1)],
            [("deleted_at", 1)],
        ]

    def is_deleted(self) -> bool:
        """Check if the staff is soft deleted."""
        return self.deleted_at is not None

    @property
    def is_online(self) -> bool:
        """Check if the staff is online."""
        return self.status == StaffStatus.ONLINE

    @property
    def is_agent(self) -> bool:
        """Check if the staff is an AI agent."""
        return self.role == StaffRole.AGENT

    @property
    def is_available_for_service(self) -> bool:
        """Check if the staff is available for accepting new visitors."""
        return self.is_active and not self.service_paused and not self.is_deleted
