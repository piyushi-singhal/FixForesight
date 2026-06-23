from fastapi import APIRouter
from typing import List
from backend.schemas.models import RecommendationResponse
from backend.services import db_service

router = APIRouter()

@router.get("/recommendations", response_model=List[RecommendationResponse])
def get_recommendations():
    return db_service.get_all_recommendations()

@router.get("/machines/{machine_id}/recommendations")
def get_machine_recommendations(machine_id: str):
    return db_service.get_machine_recommendations(machine_id)
