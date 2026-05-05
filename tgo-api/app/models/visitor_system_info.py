"""VisitorSystemInfo model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class VisitorSystemInfo(Document):
    """VisitorSystemInfo model for storing visitor system information in MongoDB."""

    visitor_id: UUID = Field(..., description="Associated visitor ID", unique=True)
    project_id: UUID = Field(..., description="Associated project ID")
    browser_name: Optional[str] = Field(None, max_length=100, description="Browser name")
    browser_version: Optional[str] = Field(None, max_length=50, description="Browser version")
    os_name: Optional[str] = Field(None, max_length=100, description="Operating system name")
    os_version: Optional[str] = Field(None, max_length=50, description="Operating system version")
    device_type: Optional[str] = Field(None, max_length=50, description="Device type (desktop, mobile, tablet)")
    screen_resolution: Optional[str] = Field(None, max_length=20, description="Screen resolution")
    language: Optional[str] = Field(None, max_length=10, description="System language")
    timezone: Optional[str] = Field(None, max_length=50, description="System timezone")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_visitor_system_infos"
        indexes = [
            [("visitor_id", 1)],
            [("project_id", 1)],
        ]
