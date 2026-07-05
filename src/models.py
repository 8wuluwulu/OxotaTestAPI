import uuid
import enum
from typing import Any, Optional
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, JSON, Enum, UUID
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class LeadStatus(str, enum.Enum):
    new = "new"
    approved = "approved"
    rejected = "rejected"

class LeadModel(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(50))
    comment: Mapped[Optional[str]] = mapped_column(String(200))
    status: Mapped[LeadStatus] = mapped_column(default=LeadStatus.new)

class OutboxEvent(Base):
    __tablename__ = "outbox"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str]
    aggregate_id: Mapped[str]
    occurred_at: Mapped[datetime] = mapped_column(default=datetime.now)
    payload: Mapped[dict[str, Any]]

class InboundEvents(Base):
    __tablename__ = "inbound_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    event_type: Mapped[str]

