"""VisitorCustomerUpdate model for MongoDB."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document
from pydantic import Field


class VisitorCustomerUpdate(Document):
    """VisitorCustomerUpdate model for tracking visitor customer information updates in MongoDB."""

    visitor_id: UUID = Field(..., description="Associated visitor ID")
    project_id: UUID = Field(..., description="Associated project ID")
    field_name: str = Field(..., max_length=100, description="Name of the updated field")
    old_value: Optional[str] = Field(None, description="Old value before update")
    new_value: Optional[str] = Field(None, description="New value after update")
    updated_by: Optional[UUID] = Field(None, description="Staff ID who made the update")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_visitor_customer_updates"
        indexes = [
            [("visitor_id", 1)],
            [("project_id", 1)],
            [("created_at", -1)],
        ]
