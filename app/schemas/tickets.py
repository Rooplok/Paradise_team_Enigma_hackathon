from datetime import datetime
from pydantic import BaseModel, Field
from app.db.models import TicketStatus, MessageDirection

class TicketCreateInbound(BaseModel):
    subject: str = ""
    customer_email: str
    from_email: str
    to_email: str
    cleaned_text: str = ""
    raw_headers: dict = Field(default_factory=dict)

class TicketOut(BaseModel):
    id: int
    subject: str
    customer_email: str
    status: TicketStatus
    category: str
    product: str
    priority: str
    ai_confidence: int
    ai_summary: str
    ai_suggested_actions: dict
    ai_draft_reply: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageOut(BaseModel):
    id: int
    ticket_id: int
    direction: MessageDirection
    from_email: str
    to_email: str
    subject: str
    cleaned_text: str
    raw_headers: dict
    created_at: datetime

    class Config:
        from_attributes = True

class TicketDetailOut(BaseModel):
    ticket: TicketOut
    messages: list[MessageOut]

class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    category: str | None = None
    product: str | None = None
    priority: str | None = None

class ApproveSendRequest(BaseModel):
    reply_text: str
    to_email: str | None = None  # если не указано, берём customer_email
    subject: str | None = None   # если не указано, берём ticket.subject

class RequestInfoRequest(BaseModel):
    questions: list[str]
    to_email: str | None = None
    subject: str | None = None

class EscalateRequest(BaseModel):
    note: str = ""