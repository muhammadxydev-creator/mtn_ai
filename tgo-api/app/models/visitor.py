"""Visitor model."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from beanie import Document, Indexed
from pydantic import Field

from app.models.platform import Platform
from app.models.visitor_ai_insight import VisitorAIInsight
from app.models.visitor_ai_profile import VisitorAIProfile
from app.models.visitor_system_info import VisitorSystemInfo


class VisitorServiceStatus(str, Enum):
    """Visitor service status enumeration.
    
    State transitions:
    - NEW: Initial state when visitor is created
    - QUEUED: Visitor is in the waiting queue
    - ACTIVE: Staff is actively serving the visitor
    - CLOSED: Service session is closed
    
    Allowed transitions:
    - NEW -> QUEUED (visitor requests human service)
    - NEW -> ACTIVE (direct assignment without queue)
    - QUEUED -> ACTIVE (staff assigned from queue)
    - ACTIVE -> CLOSED (service ends)
    - CLOSED -> QUEUED (visitor requests service again)
    - CLOSED -> ACTIVE (visitor re-engaged)
    """
    
    NEW = "new"                       # Visitor just created, no service requested
    QUEUED = "queued"                 # In waiting queue for human service
    ACTIVE = "active"                 # Currently being served by staff
    CLOSED = "closed"                 # Service session closed


# Statuses indicating visitor is unassigned (can be assigned to staff)
UNASSIGNED_STATUSES = {VisitorServiceStatus.NEW.value, VisitorServiceStatus.CLOSED.value}


class Visitor(Document):
    """Visitor model for external users/customers."""

    class Settings:
        name = "api_visitors"
        indexes = [
            "project_id",
            "platform_id",
            "platform_open_id",
            "service_status",
            "is_online",
            "deleted_at",
            [("project_id", 1), ("deleted_at", 1)],
            [("platform_id", 1), ("deleted_at", 1)],
            [("service_status", 1), ("deleted_at", 1)],
        ]

    # Primary key
    id: UUID = Field(default_factory=uuid4)

    # Foreign keys
    project_id: UUID = Field(..., description="Associated project ID for multi-tenant isolation")
    platform_id: UUID = Field(..., description="Associated platform ID")

    # Basic fields
    platform_open_id: str = Field(..., max_length=255, description="Visitor unique identifier on this platform")
    name: Optional[str] = Field(None, max_length=100, description="Visitor real name")
    nickname: Optional[str] = Field(None, max_length=100, description="Visitor nickname on this platform (English)")
    nickname_zh: Optional[str] = Field(None, max_length=100, description="Visitor nickname in Chinese")
    avatar_url: Optional[str] = Field(None, max_length=255, description="Visitor avatar URL on this platform")
    phone_number: Optional[str] = Field(None, max_length=30, description="Visitor phone number on this platform")
    email: Optional[str] = Field(None, max_length=255, description="Visitor email on this platform")
    company: Optional[str] = Field(None, max_length=255, description="Visitor company or organization")
    job_title: Optional[str] = Field(None, max_length=255, description="Visitor job title or position")
    source: Optional[str] = Field(None, max_length=255, description="Acquisition source describing how the visitor found us")
    note: Optional[str] = Field(None, description="Additional notes about the visitor")
    custom_attributes: dict = Field(default_factory=dict, description="Arbitrary custom attributes set by staff")

    # Activity tracking
    first_visit_time: datetime = Field(default_factory=datetime.utcnow, description="When the visitor first accessed the system")
    last_visit_time: datetime = Field(default_factory=datetime.utcnow, description="Visitor most recent activity/visit time")
    last_message_at: Optional[datetime] = Field(None, description="Time of the last message in the channel")
    visitor_send_count: int = Field(0, description="Total number of messages sent by the visitor")
    last_message_seq: int = Field(0, description="Sequence number of the last message in the channel")
    last_client_msg_no: Optional[str] = Field(None, max_length=100, description="Client message number of the last message in the channel")
    is_last_message_from_visitor: bool = Field(False, description="Whether the last message in the channel was sent by the visitor")
    is_last_message_from_ai: bool = Field(False, description="Whether the last message in the channel was sent by an AI")
    last_offline_time: Optional[datetime] = Field(None, description="Most recent time visitor went offline (NULL when never offline or currently online)")
    is_online: bool = Field(False, description="Whether the visitor is currently online/active")
    ai_disabled: Optional[bool] = Field(None, description="Whether AI responses are disabled for this visitor")
    ai_fallback_retry_count: int = Field(0, description="Number of failed AI fallback attempts")
    
    # Locale and network info
    timezone: Optional[str] = Field(None, max_length=50, description="Visitor timezone (e.g., 'Asia/Shanghai', 'America/New_York')")
    language: Optional[str] = Field(None, max_length=10, description="Visitor preferred language code (e.g., 'en', 'zh-CN')")
    ip_address: Optional[str] = Field(None, max_length=45, description="Visitor IP address (supports both IPv4 and IPv6)")
    
    # Geolocation (derived from IP address)
    geo_country: Optional[str] = Field(None, max_length=100, description="Country name derived from IP address")
    geo_country_code: Optional[str] = Field(None, max_length=2, description="ISO 3166-1 alpha-2 country code (e.g., 'US', 'CN')")
    geo_region: Optional[str] = Field(None, max_length=100, description="Region/state/province name")
    geo_city: Optional[str] = Field(None, max_length=100, description="City name")
    geo_isp: Optional[str] = Field(None, max_length=100, description="Internet Service Provider (available with ip2region)")
    
    # Service status
    service_status: str = Field(VisitorServiceStatus.NEW.value, max_length=20, description="Service status: new, queued, active, closed")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Soft deletion timestamp")

    def __repr__(self) -> str:
        """String representation of the visitor."""
        display_name = self.name or self.nickname or self.platform_open_id
        return f"<Visitor(id={self.id}, name='{display_name}')>"

    @property
    def is_deleted(self) -> bool:
        """Check if the visitor is soft deleted."""
        return self.deleted_at is not None

    @property
    def display_name(self) -> str:
        """Get the best available display name for the visitor."""
        return self.name or self.nickname or self.platform_open_id

    @property
    def is_unassigned(self) -> bool:
        """Check if visitor is unassigned (can be assigned to staff)."""
        return self.service_status in UNASSIGNED_STATUSES

    def set_status_queued(self) -> None:
        """Set visitor status to QUEUED."""
        self.service_status = VisitorServiceStatus.QUEUED.value
        self.updated_at = datetime.utcnow()

    def set_status_active(self) -> None:
        """Set visitor status to ACTIVE."""
        self.service_status = VisitorServiceStatus.ACTIVE.value
        self.updated_at = datetime.utcnow()

    def set_status_closed(self) -> None:
        """Set visitor status to CLOSED."""
        self.service_status = VisitorServiceStatus.CLOSED.value
        self.updated_at = datetime.utcnow()
