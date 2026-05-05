"""Platform model for MongoDB."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import Field


class PlatformType(str, Enum):
    """Platform type enumeration."""

    WEBSITE = "website"
    WECHAT = "wechat"
    WECHAT_PERSONAL = "wechat_personal"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    EMAIL = "email"
    SMS = "sms"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    DISCORD = "discord"
    SLACK = "slack"
    TEAMS = "teams"
    PHONE = "phone"
    DOUYIN = "douyin"
    TIKTOK = "tiktok"
    CUSTOM = "custom"
    WECOM = "wecom"
    WECOM_BOT = "wecom_bot"
    FEISHU_BOT = "feishu_bot"
    DINGTALK_BOT = "dingtalk_bot"


class PlatformSyncStatus(str, Enum):
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"


class PlatformAIMode(str, Enum):
    """Platform AI mode enumeration."""
    AUTO = "auto"
    ASSIST = "assist"
    OFF = "off"


class Platform(Document):
    """Platform model for communication platforms in MongoDB."""

    project_id: UUID = Field(..., description="Associated project ID")
    name: Optional[str] = Field(None, description="Platform name")
    type: str = Field(..., description="Platform type from predefined enum")
    api_key: Optional[str] = Field(None, description="Platform-specific API key")
    config: Optional[dict] = Field(None, description="Platform-specific configuration")
    is_active: bool = Field(default=True, description="Whether platform is active")
    agent_id: Optional[UUID] = Field(None, description="AI Agent ID")
    ai_mode: Optional[str] = Field(default=PlatformAIMode.AUTO.value, description="AI mode")
    fallback_to_ai_timeout: Optional[int] = Field(default=0, description="Timeout in seconds")
    is_used: bool = Field(default=False, description="Whether platform has been used")
    used_website_url: Optional[str] = Field(None, description="Website URL where first used")
    used_website_title: Optional[str] = Field(None, description="Website title where first used")
    logo_path: Optional[str] = Field(None, description="Relative path to logo file")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    sync_status: str = Field(default=PlatformSyncStatus.PENDING.value, description="Sync status")
    last_synced_at: Optional[datetime] = None
    sync_error: Optional[str] = Field(None, description="Last sync error message")
    sync_retry_count: int = Field(default=0, description="Number of sync retry attempts")

    class Settings:
        name = "platforms"
        indexes = [
            [("project_id", 1)],
            [("type", 1)],
            [("deleted_at", 1)],
            [("created_at", -1)],
        ]

    def is_deleted(self) -> bool:
        """Check if the platform is soft deleted."""
        return self.deleted_at is not None
