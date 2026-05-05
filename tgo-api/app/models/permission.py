"""Permission models for MongoDB."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from beanie import Document, Link
from pydantic import Field


class Permission(Document):
    """Permission model for role-based access control in MongoDB."""

    project_id: UUID = Field(..., description="Associated project ID")
    name: str = Field(..., max_length=100, description="Permission name")
    description: Optional[str] = Field(None, description="Permission description")
    resource: str = Field(..., max_length=100, description="Resource type")
    actions: List[str] = Field(default_factory=list, description="Allowed actions")
    role: str = Field(..., max_length=50, description="Role this permission applies to")
    is_active: bool = Field(default=True, description="Whether permission is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "api_permissions"
        indexes = [
            [("project_id", 1)],
            [("role", 1)],
            [("resource", 1)],
            [("is_active", 1)],
            [("deleted_at", 1)],
        ]

    def is_deleted(self) -> bool:
        """Check if the permission is soft deleted."""
        return self.deleted_at is not None


class RolePermission(Document):
    """Global role permission mapping in MongoDB."""

    role: str = Field(..., max_length=50, description="Role name")
    permission_id: str = Field(..., description="Reference to Permission ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "role_permissions"
        indexes = [
            [("role", 1)],
            [("permission_id", 1)],
            [("deleted_at", 1)],
        ]


class ProjectRolePermission(Document):
    """Project-specific role permission mapping in MongoDB."""

    project_id: UUID = Field(..., description="Project ID")
    role: str = Field(..., max_length=50, description="Role name")
    permission_id: str = Field(..., description="Reference to Permission ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "project_role_permissions"
        indexes = [
            [("project_id", 1)],
            [("role", 1)],
            [("permission_id", 1)],
            [("deleted_at", 1)],
        ]
