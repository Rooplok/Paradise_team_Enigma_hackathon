from pydantic import BaseModel, Field

class Page(BaseModel):
    items: list
    total: int
    limit: int
    offset: int

class Ok(BaseModel):
    ok: bool = True

class IdResponse(BaseModel):
    id: int