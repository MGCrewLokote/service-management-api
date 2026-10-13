"""API contracts and request validation."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: TicketStatus = TicketStatus.open
    priority: TicketPriority = TicketPriority.medium
    assigned_to: str | None = Field(default=None, max_length=120)


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assigned_to: str | None = Field(default=None, max_length=120)


class TicketRead(TicketCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class TicketPage(BaseModel):
    items: list[TicketRead]
    total: int
    limit: int
    offset: int
