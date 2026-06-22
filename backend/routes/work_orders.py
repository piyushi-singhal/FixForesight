from fastapi import APIRouter
from typing import List
from backend.schemas.models import WorkOrderRequest, WorkOrderResponse
from backend.services import db_service

router = APIRouter()

@router.get("/work-orders", response_model=List[WorkOrderResponse])
def get_work_orders():
    return db_service.get_all_work_orders()

@router.post("/work-orders")
def post_work_order(req: WorkOrderRequest):
    wo_id = db_service.create_work_order(req.machine_id, req.priority, req.action_required)
    return {"status": "created", "work_order_id": wo_id}
