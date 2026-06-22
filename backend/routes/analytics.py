from fastapi import APIRouter
from backend.schemas.models import AnalyticsResponse
from backend.services import db_service

router = APIRouter()

@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics():
    return db_service.get_analytics()
