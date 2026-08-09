from fastapi import APIRouter, HTTPException, BackgroundTasks
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

@router.post("/machines/{machine_id}/simulate")
def simulate_machine(machine_id: str, background_tasks: BackgroundTasks, count: int = 10, interval: float = 1.0):
    try:
        from sensor_simulator import SensorSimulator
    except ImportError:
        import sys
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, os.path.join(base_dir, "src"))
        from sensor_simulator import SensorSimulator
        
    def run_sim():
        sim = SensorSimulator()
        sim.simulate_to_sqs(machine_id=machine_id, interval_seconds=interval, num_events=count)
        
    background_tasks.add_task(run_sim)
    return {"status": "simulation_started", "machine_id": machine_id, "events_count": count}
