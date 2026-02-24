import smtplib
from email.message import EmailMessage
from app.core.config import settings

def send_email(to_email: str, subject: str, body_text: str, in_reply_to: str | None = None, references: str | None = None) -> None:
    msg = EmailMessage()
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    if references:
        msg["References"] = references

    msg.set_content(body_text)

    if settings.SMTP_USE_TLS:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
    else:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)

    try:
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
    finally:
        server.quit()