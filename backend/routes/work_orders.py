from fastapi import APIRouter
from backend.schemas.models import WorkOrderRequest
from backend.services import db_service

router = APIRouter()

@router.post("/work-orders")
def post_work_order(req: WorkOrderRequest):
    wo_id = db_service.create_work_order(req.machine_id, req.priority, req.action_required)
    return {"status": "created", "work_order_id": wo_id}
