from datetime import datetime
from pydantic import BaseModel, Field

class KbDocumentCreate(BaseModel):
    title: str
    body: str
    tags: list[str] = Field(default_factory=list)
    language: str = "ru"
    status: str = "active"

class KbDocumentOut(BaseModel):
    id: int
    title: str
    body: str
    tags: list[str]
    language: str
    status: str
    updated_at: datetime

    class Config:
        from_attributes = True

class KbSearchHit(BaseModel):
    id: int
    title: str
    rank: float
    snippet: str

class KbSearchResponse(BaseModel):
    query: str
    hits: list[KbSearchHit]