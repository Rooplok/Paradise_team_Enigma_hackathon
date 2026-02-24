from pydantic import BaseModel

class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body_text: str
    in_reply_to: str | None = None
    references: str | None = None