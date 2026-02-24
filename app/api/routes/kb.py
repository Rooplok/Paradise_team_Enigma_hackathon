from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.security import require_api_key
from app.schemas.kb import KbDocumentCreate, KbDocumentOut, KbSearchResponse
from app.services.kb import create_kb_document, update_kb_document, get_kb_document, search_kb

router = APIRouter(prefix="/kb", tags=["kb"], dependencies=[Depends(require_api_key)])

@router.post("/documents", response_model=KbDocumentOut)
def kb_create(payload: KbDocumentCreate, db: Session = Depends(get_db)):
    doc = create_kb_document(db, payload.title, payload.body, payload.tags, payload.language, payload.status)
    return doc

@router.put("/documents/{doc_id}", response_model=KbDocumentOut)
def kb_update(doc_id: int, payload: KbDocumentCreate, db: Session = Depends(get_db)):
    try:
        doc = update_kb_document(db, doc_id, payload.title, payload.body, payload.tags, payload.language, payload.status)
        return doc
    except ValueError:
        raise HTTPException(status_code=404, detail="KB document not found")

@router.get("/documents/{doc_id}", response_model=KbDocumentOut)
def kb_get(doc_id: int, db: Session = Depends(get_db)):
    doc = get_kb_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="KB document not found")
    return doc

@router.get("/search", response_model=KbSearchResponse)
def kb_search(q: str, limit: int = 5, db: Session = Depends(get_db)):
    hits = search_kb(db, query=q, limit=min(max(limit, 1), 20))
    return {"query": q, "hits": hits}