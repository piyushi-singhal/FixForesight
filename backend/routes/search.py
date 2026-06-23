from fastapi import APIRouter
from backend.services import db_service

router = APIRouter()

@router.get("/search")
def search_incidents(q: str = "*:*"):
    return db_service.search_incidents(q)
