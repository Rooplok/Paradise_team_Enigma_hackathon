import io
import csv
from sqlalchemy.orm import Session
from sqlalchemy import select
from openpyxl import Workbook
from app.db.models import Ticket

def export_tickets_csv(db: Session) -> bytes:
    tickets = db.scalars(select(Ticket).order_by(Ticket.updated_at.desc())).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "subject", "customer_email", "status", "category", "product", "priority", "ai_confidence", "updated_at"])
    for t in tickets:
        writer.writerow([t.id, t.subject, t.customer_email, t.status, t.category, t.product, t.priority, t.ai_confidence, t.updated_at.isoformat()])
    return buf.getvalue().encode("utf-8")

def export_tickets_xlsx(db: Session) -> bytes:
    tickets = db.scalars(select(Ticket).order_by(Ticket.updated_at.desc())).all()
    wb = Workbook()
    ws = wb.active
    ws.title = "tickets"
    ws.append(["id", "subject", "customer_email", "status", "category", "product", "priority", "ai_confidence", "updated_at"])
    for t in tickets:
        ws.append([t.id, t.subject, t.customer_email, str(t.status), t.category, t.product, t.priority, t.ai_confidence, t.updated_at.isoformat()])

    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()