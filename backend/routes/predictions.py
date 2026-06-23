from fastapi import APIRouter
from typing import List
from backend.schemas.models import PredictionResponse
from backend.services import db_service

router = APIRouter()

@router.get("/predictions", response_model=List[PredictionResponse])
def get_predictions():
    return db_service.get_all_predictions()

@router.post("/predictions/pipeline")
def run_pipeline(limit: int = 100):
    count = db_service.run_predictions_pipeline(limit=limit)
    return {"status": "success", "processed_records": count}

