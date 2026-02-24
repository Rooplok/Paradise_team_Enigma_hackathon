from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from app.core.config import settings
from app.db.models import KbDocument

def create_kb_document(db: Session, title: str, body: str, tags: list[str], language: str, status: str) -> KbDocument:
    doc = KbDocument(title=title, body=body, tags=tags, language=language, status=status)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def update_kb_document(db: Session, doc_id: int, title: str, body: str, tags: list[str], language: str, status: str) -> KbDocument:
    doc = db.get(KbDocument, doc_id)
    if not doc:
        raise ValueError("KB document not found")
    doc.title = title
    doc.body = body
    doc.tags = tags
    doc.language = language
    doc.status = status
    db.commit()
    db.refresh(doc)
    return doc

def get_kb_document(db: Session, doc_id: int) -> KbDocument | None:
    return db.get(KbDocument, doc_id)

def search_kb(db: Session, query: str, limit: int = 5, language: str | None = None) -> list[dict]:
    """
    Full Text Search via PostgreSQL:
    - websearch_to_tsquery for natural queries
    - ts_rank_cd for ranking
    - ts_headline for snippet
    """
    lang = (language or settings.KB_TS_CONFIG).strip() or "russian"

    # Note: We rely on kb_documents.search_tsv being a real tsvector (created in migration).
    sql = sql_text(
        """
        WITH q AS (
          SELECT websearch_to_tsquery(:ts_config, :query) AS query
        )
        SELECT
          d.id,
          d.title,
          ts_rank_cd(d.search_tsv, q.query) AS rank,
          ts_headline(:ts_config, d.body, q.query, 'MaxWords=28, MinWords=10, ShortWord=3, MaxFragments=2, FragmentDelimiter= … ') AS snippet
        FROM kb_documents d, q
        WHERE d.status = 'active'
          AND d.search_tsv @@ q.query
        ORDER BY rank DESC
        LIMIT :limit;
        """
    )
    rows = db.execute(sql, {"ts_config": lang, "query": query, "limit": limit}).mappings().all()
    return [dict(r) for r in rows]