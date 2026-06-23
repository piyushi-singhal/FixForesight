from sqlalchemy.orm import Session
from src.backend_copy.database.models import Machine, Prediction, Recommendation, Alert, PartInventory, WorkOrder
from datetime import datetime

def get_machines(db: Session):
    return db.query(Machine).all()

def get_machine(db: Session, machine_id: str):
    return db.query(Machine).filter(Machine.machine_id == machine_id).first()

def get_predictions(db: Session):
    return db.query(Prediction).all()

def get_recommendations(db: Session):
    return db.query(Recommendation).all()

def get_machine_recommendation(db: Session, machine_id: str):
    return db.query(Recommendation).filter(Recommendation.machine_id == machine_id).first()

def get_work_orders(db: Session):
    return db.query(WorkOrder).all()

def get_alerts(db: Session):
    return db.query(Alert).order_by(Alert.created_at.desc()).all()

def get_parts_inventory(db: Session):
    return db.query(PartInventory).all()

def create_work_order(db: Session, machine_id: str, priority: str, action_required: str):
    db_wo = WorkOrder(
        machine_id=machine_id,
        priority=priority,
        action_required=action_required,
        status="open",
        created_at=datetime.utcnow()
    )
    db.add(db_wo)
    db.commit()
    db.refresh(db_wo)
    return db_wo.id
