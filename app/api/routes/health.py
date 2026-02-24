from fastapi import APIRouter
from app.schemas.common import Ok

router = APIRouter(tags=["health"])

@router.get("/health", response_model=Ok)
def health():
    return Ok(ok=True)