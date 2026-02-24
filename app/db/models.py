import enum
from datetime import datetime
from sqlalchemy import (
    String, Text, DateTime, Enum, Integer, ForeignKey, Boolean, JSON, func, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TicketStatus(str, enum.Enum):
    new = "new"
    needs_info = "needs_info"
    waiting_customer = "waiting_customer"
    solved = "solved"
    escalated = "escalated"


class MessageDirection(str, enum.Enum):
    inbound = "inbound"
    outbound = "outbound"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject: Mapped[str] = mapped_column(String(512), default="")
    customer_email: Mapped[str] = mapped_column(String(320), default="")
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.new)

    category: Mapped[str] = mapped_column(String(128), default="")
    product: Mapped[str] = mapped_column(String(128), default="")
    priority: Mapped[str] = mapped_column(String(32), default="medium")  # low/medium/high

    ai_confidence: Mapped[float] = mapped_column(Integer, default=0)  # 0..100 for MVP
    ai_summary: Mapped[str] = mapped_column(Text, default="")
    ai_suggested_actions: Mapped[dict] = mapped_column(JSON, default=dict)
    ai_draft_reply: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    messages: Mapped[list["Message"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")
    ai_runs: Mapped[list["AiRun"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    direction: Mapped[MessageDirection] = mapped_column(Enum(MessageDirection))
    from_email: Mapped[str] = mapped_column(String(320), default="")
    to_email: Mapped[str] = mapped_column(String(320), default="")
    subject: Mapped[str] = mapped_column(String(512), default="")

    raw_headers: Mapped[dict] = mapped_column(JSON, default=dict)
    cleaned_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped["Ticket"] = relationship(back_populates="messages")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="message", cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(512), default="")
    mime_type: Mapped[str] = mapped_column(String(128), default="")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    storage_path: Mapped[str] = mapped_column(String(1024), default="")

    message: Mapped["Message"] = relationship(back_populates="attachments")


class AiRun(Base):
    __tablename__ = "ai_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))

    model_versions: Mapped[dict] = mapped_column(JSON, default=dict)
    outputs: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped["Ticket"] = relationship(back_populates="ai_runs")


# KB (Variant 3: Full-Text Search)
class KbDocument(Base):
    __tablename__ = "kb_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)  # MVP: JSON array
    language: Mapped[str] = mapped_column(String(16), default="ru")
    status: Mapped[str] = mapped_column(String(32), default="active")  # active/archived
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # We'll store tsvector in DB via migration SQL (generated column) for best performance.
    # Here we keep it as TEXT placeholder for SQLAlchemy mapping safety; real type is TSVECTOR.
    search_tsv: Mapped[str] = mapped_column(Text, default="")  # 실제 tsvector via migration

Index("ix_tickets_status", Ticket.status)
Index("ix_tickets_updated_at", Ticket.updated_at)
Index("ix_messages_ticket_id", Message.ticket_id)
Index("ix_kb_documents_status", KbDocument.status)