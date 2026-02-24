from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.models import Ticket, Message, MessageDirection, TicketStatus, AiRun
from app.services.ai import analyze_message
from app.services.kb import search_kb

def create_ticket_from_inbound(
    db: Session,
    subject: str,
    customer_email: str,
    from_email: str,
    to_email: str,
    cleaned_text: str,
    raw_headers: dict,
) -> Ticket:
    ticket = Ticket(subject=subject, customer_email=customer_email, status=TicketStatus.new)
    db.add(ticket)
    db.flush()

    msg = Message(
        ticket_id=ticket.id,
        direction=MessageDirection.inbound,
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        cleaned_text=cleaned_text,
        raw_headers=raw_headers or {},
    )
    db.add(msg)
    db.flush()

    # Run AI analysis (MVP)
    ai = analyze_message(subject, cleaned_text)

    # KB search (Variant 3)
    kb_hits = search_kb(db, query=f"{subject}\n{cleaned_text}"[:800], limit=5)

    ticket.category = ai["category"]
    ticket.product = ai.get("product", "")
    ticket.priority = ai["priority"]
    ticket.ai_summary = ai["summary"]
    ticket.ai_draft_reply = ai["draft_reply"]
    ticket.ai_suggested_actions = {
        **ai.get("suggested_actions", {}),
        "kb_hits": [{"id": h["id"], "title": h["title"], "rank": float(h["rank"]), "snippet": h["snippet"]} for h in kb_hits],
        "entities": ai.get("entities", {}),
    }
    ticket.ai_confidence = int(ai["confidence"])

    run = AiRun(
        ticket_id=ticket.id,
        model_versions=ai.get("model_versions", {}),
        outputs={
            "summary": ai["summary"],
            "draft_reply": ai["draft_reply"],
            "entities": ai.get("entities", {}),
            "missing_info": ai.get("missing_info", []),
            "kb_hits": kb_hits,
        },
        confidence=int(ai["confidence"]),
    )
    db.add(run)

    # status suggestion
    if ai.get("suggested_actions", {}).get("next_step") == "request_info":
        ticket.status = TicketStatus.needs_info

    db.commit()
    db.refresh(ticket)
    return ticket

def list_tickets(db: Session, limit: int, offset: int, status: str | None, priority: str | None, q: str | None):
    stmt = select(Ticket)
    if status:
        stmt = stmt.where(Ticket.status == status)
    if priority:
        stmt = stmt.where(Ticket.priority == priority)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((Ticket.subject.ilike(like)) | (Ticket.customer_email.ilike(like)))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(stmt.order_by(Ticket.updated_at.desc()).limit(limit).offset(offset)).all()
    return items, int(total)

def get_ticket_detail(db: Session, ticket_id: int) -> tuple[Ticket | None, list[Message]]:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        return None, []
    msgs = db.scalars(select(Message).where(Message.ticket_id == ticket_id).order_by(Message.created_at.asc())).all()
    return ticket, msgs

def update_ticket(db: Session, ticket_id: int, **fields) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise ValueError("Ticket not found")
    for k, v in fields.items():
        if v is not None and hasattr(ticket, k):
            setattr(ticket, k, v)
    db.commit()
    db.refresh(ticket)
    return ticket

def add_outbound_message(db: Session, ticket_id: int, to_email: str, subject: str, body_text: str) -> Message:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise ValueError("Ticket not found")

    msg = Message(
        ticket_id=ticket_id,
        direction=MessageDirection.outbound,
        from_email="",  # can be SMTP_USER at UI level if needed
        to_email=to_email,
        subject=subject,
        cleaned_text=body_text,
        raw_headers={},
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg