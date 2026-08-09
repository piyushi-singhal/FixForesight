from fastapi import APIRouter
from typing import List
from backend.schemas.models import WorkOrderRequest, WorkOrderResponse, WorkOrderStatusUpdate
from backend.services import db_service
from fastapi import HTTPException

router = APIRouter()

@router.get("/work-orders", response_model=List[WorkOrderResponse])
def get_work_orders():
    return db_service.get_all_work_orders()

@router.post("/work-orders")
def post_work_order(req: WorkOrderRequest):
    wo_id = db_service.create_work_order(
        machine_id=req.machine_id,
        priority=req.priority,
        action_required=req.action_required,
        recommendation_id=req.recommendation_id
    )
    return {"status": "created", "work_order_id": wo_id}

@router.patch("/work-orders/{id}/status")
def patch_work_order_status(id: int, req: WorkOrderStatusUpdate):
    try:
        updated_wo = db_service.update_work_order_status(id, req.status)
        return {"status": "success", "work_order_id": updated_wo.id, "new_status": updated_wo.status}
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
