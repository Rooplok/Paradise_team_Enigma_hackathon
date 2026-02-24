from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.security import require_api_key
from app.schemas.common import Page, IdResponse, Ok
from app.schemas.tickets import (
    TicketCreateInbound, TicketOut, TicketDetailOut, TicketUpdate,
    ApproveSendRequest, RequestInfoRequest, EscalateRequest
)
from app.services.tickets import (
    create_ticket_from_inbound, list_tickets, get_ticket_detail, update_ticket, add_outbound_message
)
from app.services.email import send_email

router = APIRouter(prefix="/tickets", tags=["tickets"], dependencies=[Depends(require_api_key)])

@router.post("/inbound", response_model=IdResponse)
def ingest_inbound(payload: TicketCreateInbound, db: Session = Depends(get_db)):
    ticket = create_ticket_from_inbound(
        db=db,
        subject=payload.subject,
        customer_email=payload.customer_email,
        from_email=payload.from_email,
        to_email=payload.to_email,
        cleaned_text=payload.cleaned_text,
        raw_headers=payload.raw_headers,
    )
    return {"id": ticket.id}

@router.get("", response_model=Page)
def tickets_list(
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    priority: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    limit = min(max(limit, 1), 200)
    offset = max(offset, 0)
    items, total = list_tickets(db, limit=limit, offset=offset, status=status, priority=priority, q=q)
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.get("/{ticket_id}", response_model=TicketDetailOut)
def ticket_detail(ticket_id: int, db: Session = Depends(get_db)):
    ticket, msgs = get_ticket_detail(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"ticket": ticket, "messages": msgs}

@router.patch("/{ticket_id}", response_model=TicketOut)
def ticket_patch(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)):
    try:
        ticket = update_ticket(
            db,
            ticket_id,
            status=payload.status,
            category=payload.category,
            product=payload.product,
            priority=payload.priority,
        )
        return ticket
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")

@router.post("/{ticket_id}/approve-send", response_model=Ok)
def approve_and_send(ticket_id: int, payload: ApproveSendRequest, db: Session = Depends(get_db)):
    ticket, _ = get_ticket_detail(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    to_email = payload.to_email or ticket.customer_email
    subject = payload.subject or ticket.subject or "Support request"

    # Send
    send_email(to_email=to_email, subject=subject, body_text=payload.reply_text)

    # Save outbound message and update ticket status
    add_outbound_message(db, ticket_id, to_email=to_email, subject=subject, body_text=payload.reply_text)
    update_ticket(db, ticket_id, status="waiting_customer")

    return {"ok": True}

@router.post("/{ticket_id}/request-info", response_model=Ok)
def request_info(ticket_id: int, payload: RequestInfoRequest, db: Session = Depends(get_db)):
    ticket, _ = get_ticket_detail(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    to_email = payload.to_email or ticket.customer_email
    subject = payload.subject or (ticket.subject or "Support request")

    body = (
        "Здравствуйте!\n\n"
        "Чтобы быстрее помочь, уточните, пожалуйста:\n"
        + "\n".join(f"- {q}" for q in payload.questions)
        + "\n\nС уважением,\nТехподдержка"
    )

    send_email(to_email=to_email, subject=subject, body_text=body)
    add_outbound_message(db, ticket_id, to_email=to_email, subject=subject, body_text=body)
    update_ticket(db, ticket_id, status="needs_info")

    return {"ok": True}

@router.post("/{ticket_id}/escalate", response_model=Ok)
def escalate(ticket_id: int, payload: EscalateRequest, db: Session = Depends(get_db)):
    ticket, _ = get_ticket_detail(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    update_ticket(db, ticket_id, status="escalated")
    return {"ok": True}