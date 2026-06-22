from fastapi import APIRouter
from backend.schemas.models import DashboardResponse
from backend.services import db_service

router = APIRouter()

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard():
    return db_service.get_dashboard_data()
