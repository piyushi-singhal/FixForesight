from fastapi import APIRouter, HTTPException
from typing import List
from backend.schemas.models import MachineResponse
from backend.services import db_service

router = APIRouter()

@router.get("/machines", response_model=List[MachineResponse])
def get_machines():
    return db_service.get_all_machines()

@router.get("/machines/{machine_id}/risk")
def get_machine_risk(machine_id: str):
    data = db_service.get_machine_risk(machine_id)
    if not data:
        raise HTTPException(status_code=404, detail="Machine not found")
    return data
