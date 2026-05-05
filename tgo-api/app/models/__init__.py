"""MongoDB Models for the application."""

from app.models.project import Project
from app.models.platform import Platform, PlatformType, PlatformSyncStatus, PlatformAIMode
from app.models.visitor import Visitor, VisitorServiceStatus, UNASSIGNED_STATUSES
from app.models.staff import Staff, StaffRole, StaffStatus
from app.models.tag import Tag, TagCategory
from app.models.visitor_tag import VisitorTag
from app.models.visitor_session import VisitorSession
from app.models.visitor_activity import VisitorActivity
from app.models.visitor_ai_profile import VisitorAIProfile
from app.models.visitor_ai_insight import VisitorAIInsight
from app.models.visitor_system_info import VisitorSystemInfo
from app.models.visitor_waiting_queue import VisitorWaitingQueue
from app.models.visitor_assignment_rule import VisitorAssignmentRule
from app.models.visitor_assignment_history import VisitorAssignmentHistory
from app.models.visitor_customer_update import VisitorCustomerUpdate
from app.models.ai_provider import AIProvider, AIProviderType
from app.models.ai_model import AIModel, AIModelType
from app.models.project_ai_config import ProjectAIConfig
from app.models.project_onboarding import ProjectOnboardingProgress
from app.models.ai_provider_default_model import AIProviderDefaultModel
from app.models.system_setup import SystemSetup
from app.models.store_credential import StoreCredential
from app.models.permission import Permission
from app.models.channel_member import ChannelMember
from app.models.channel_memory_clearance import ChannelMemoryClearance
from app.models.chat_file import ChatFile

__all__ = [
    "Project",
    "Platform",
    "PlatformType",
    "PlatformSyncStatus",
    "PlatformAIMode",
    "Visitor",
    "VisitorServiceStatus",
    "UNASSIGNED_STATUSES",
    "Staff",
    "StaffRole",
    "StaffStatus",
    "Tag",
    "TagCategory",
    "VisitorTag",
    "VisitorSession",
    "VisitorActivity",
    "VisitorAIProfile",
    "VisitorAIInsight",
    "VisitorSystemInfo",
    "VisitorWaitingQueue",
    "VisitorAssignmentRule",
    "VisitorAssignmentHistory",
    "VisitorCustomerUpdate",
    "AIProvider",
    "AIProviderType",
    "AIModel",
    "AIModelType",
    "ProjectAIConfig",
    "ProjectOnboardingProgress",
    "AIProviderDefaultModel",
    "SystemSetup",
    "StoreCredential",
    "Permission",
    "ChannelMember",
    "ChannelMemoryClearance",
    "ChatFile",
]
