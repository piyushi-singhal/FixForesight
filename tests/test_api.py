# tests/test_api.py
"""
FastAPI Route Schema and Logic tests.
"""

import os
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "postgres" in data
    assert "localstack" in data
    assert "solr" in data

def test_get_machines():
    response = client.get("/machines")
    assert response.status_code == 200
    machines = response.json()
    assert isinstance(machines, list)

def test_get_predictions():
    response = client.get("/predictions")
    assert response.status_code == 200
    preds = response.json()
    assert isinstance(preds, list)

def test_work_orders_flow():
    # 1. Create a work order
    payload = {
        "machine_id": "M101",
        "priority": "High",
        "action_required": "Pytest verification of work order creation",
        "recommendation_id": None
    }
    response = client.post("/work-orders", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    wo_id = data["work_order_id"]

    # 2. Patch status to in_progress
    response = client.patch(f"/work-orders/{wo_id}/status", json={"status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["new_status"] == "in_progress"

    # 3. Patch status to completed
    response = client.patch(f"/work-orders/{wo_id}/status", json={"status": "completed"})
    assert response.status_code == 200
    assert response.json()["new_status"] == "completed"

    # 4. Patch status to invalid value (should return 422 validation error)
    response = client.patch(f"/work-orders/{wo_id}/status", json={"status": "banana"})
    assert response.status_code == 422


def test_model_monitoring():
    response = client.get("/analytics/model-monitoring")
    assert response.status_code == 200
    metrics = response.json()
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        assert key in metrics
        assert isinstance(metrics[key], float)
        assert 0.0 <= metrics[key] <= 1.0


