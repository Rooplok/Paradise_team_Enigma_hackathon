from fastapi import APIRouter, Depends
from app.core.security import require_api_key
from app.schemas.common import Ok
from app.schemas.email import SendEmailRequest
from app.services.email import send_email

router = APIRouter(prefix="/email", tags=["email"], dependencies=[Depends(require_api_key)])

@router.post("/send", response_model=Ok)
def api_send_email(payload: SendEmailRequest):
    send_email(
        to_email=payload.to_email,
        subject=payload.subject,
        body_text=payload.body_text,
        in_reply_to=payload.in_reply_to,
        references=payload.references,
    )
    return {"ok": True}