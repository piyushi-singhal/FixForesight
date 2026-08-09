# tests_api_e2e.py
"""
End-to-End Integration Test Suite for FixForesight
Validates the ML -> PostgreSQL -> FastAPI flow by calling actual REST API endpoints.
"""

import sys
import requests

API_BASE = "http://127.0.0.1:8000"

def test_e2e_flow():
    print("=" * 80)
    print("STARTING END-TO-END API INTEGRATION TEST FLOW")
    print("=" * 80 + "\n")

    # 1. Trigger prediction pipeline
    print("1. Triggering predictions pipeline...")
    r = requests.post(f"{API_BASE}/predictions/pipeline?limit=5")
    assert r.status_code == 200, f"Pipeline failed: {r.text}"
    data = r.json()
    assert data["status"] == "success"
    print(f"   ✓ POST /predictions/pipeline passed. Processed: {data['processed_records']}")

    # 2. Get predictions
    print("\n2. Fetching failure predictions...")
    r = requests.get(f"{API_BASE}/predictions")
    assert r.status_code == 200, f"Predictions fetch failed: {r.text}"
    preds = r.json()
    assert len(preds) > 0, "No predictions found"
    print(f"   ✓ GET /predictions passed. Found {len(preds)} prediction entries.")

    # 3. Get machines
    print("\n3. Fetching fleet machines...")
    r = requests.get(f"{API_BASE}/machines")
    assert r.status_code == 200, f"Machines fetch failed: {r.text}"
    machines = r.json()
    assert len(machines) > 0, "No machines found"
    print(f"   ✓ GET /machines passed. Found {len(machines)} machine entries.")

    # 4. Create a work order
    print("\n4. Creating a work order...")
    payload = {
        "machine_id": "M101",
        "priority": "High",
        "action_required": "Replace worn parts during shutdown",
        "recommendation_id": None
    }
    r = requests.post(f"{API_BASE}/work-orders", json=payload)
    assert r.status_code == 200, f"Work order creation failed: {r.text}"
    res = r.json()
    assert res["status"] == "created"
    wo_id = res["work_order_id"]
    print(f"   ✓ POST /work-orders passed. Created Work Order ID: {wo_id}")

    # 5. Patch work order status to in_progress
    print(f"\n5. Patching status of Work Order {wo_id} to in_progress...")
    r = requests.patch(f"{API_BASE}/work-orders/{wo_id}/status", json={"status": "in_progress"})
    assert r.status_code == 200, f"Status patch failed: {r.text}"
    assert r.json()["new_status"] == "in_progress"
    print("   ✓ PATCH /work-orders status to in_progress passed")

    # 6. Complete the work order status
    print(f"\n6. Patching status of Work Order {wo_id} to completed...")
    r = requests.patch(f"{API_BASE}/work-orders/{wo_id}/status", json={"status": "completed"})
    assert r.status_code == 200, f"Status completion failed: {r.text}"
    assert r.json()["new_status"] == "completed"
    print("   ✓ PATCH /work-orders status to completed passed")

    print("\n" + "=" * 80)
    print("ALL END-TO-END API TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_e2e_flow()
    except AssertionError as ae:
        print(f"\n❌ Test Assertion Failure: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Test Failure: {e}")
        sys.exit(1)
