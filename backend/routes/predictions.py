from fastapi import APIRouter
from typing import List
from backend.schemas.models import PredictionResponse
from backend.services import db_service

router = APIRouter()

@router.get("/predictions", response_model=List[PredictionResponse])
def get_predictions():
    return db_service.get_all_predictions()
