from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.security import require_api_key
from app.services.export import export_tickets_csv, export_tickets_xlsx

router = APIRouter(prefix="/export", tags=["export"], dependencies=[Depends(require_api_key)])

@router.get("/tickets.csv")
def export_csv(db: Session = Depends(get_db)):
    data = export_tickets_csv(db)
    return Response(content=data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=tickets.csv"})

@router.get("/tickets.xlsx")
def export_xlsx(db: Session = Depends(get_db)):
    data = export_tickets_xlsx(db)
    return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=tickets.xlsx"})