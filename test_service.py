import sys
import os

# Set cache directories to workspace-local paths to prevent sandbox violations
workspace_dir = "/Users/piyushisinghal/Downloads/FixForesight"
cache_dir = os.path.join(workspace_dir, "tmp", "cache")
os.makedirs(cache_dir, exist_ok=True)

os.environ["DATABASE_URL"] = "sqlite:///pdm_db.db"
os.environ["XDG_CACHE_HOME"] = cache_dir
os.environ["JOBLIB_TEMP_FOLDER"] = cache_dir
os.environ["MPLCONFIGDIR"] = cache_dir
os.environ["PYTHON_EGG_CACHE"] = cache_dir

# Add workspace directory and virtual environment packages to path
sys.path.insert(0, "/Users/piyushisinghal/Downloads/FixForesight/venv/lib/python3.14/site-packages")
sys.path.insert(0, workspace_dir)

from backend.services import db_service

print("=== Testing db_service fallback logic ===")

# Test 1: get_dashboard_data
print("\n1. Testing get_dashboard_data():")
try:
    dash = db_service.get_dashboard_data()
    print("SUCCESS:", dash)
except Exception as e:
    print("FAILED:", e)

# Test 2: get_all_machines
print("\n2. Testing get_all_machines():")
try:
    machines = db_service.get_all_machines()
    print("SUCCESS (showing first machine):", machines[0])
    print(f"Total machines returned: {len(machines)}")
except Exception as e:
    print("FAILED:", e)

# Test 3: get_all_predictions
print("\n3. Testing get_all_predictions():")
try:
    predictions = db_service.get_all_predictions()
    print("SUCCESS (showing first prediction):", predictions[0])
    print(f"Total predictions returned: {len(predictions)}")
except Exception as e:
    print("FAILED:", e)

# Test 4: get_all_recommendations
print("\n4. Testing get_all_recommendations():")
try:
    recommendations = db_service.get_all_recommendations()
    print("SUCCESS (showing first recommendation):", recommendations[0] if recommendations else "None")
    print(f"Total recommendations returned: {len(recommendations)}")
except Exception as e:
    print("FAILED:", e)

# Test 5: get_all_work_orders
print("\n5. Testing get_all_work_orders():")
try:
    work_orders = db_service.get_all_work_orders()
    print("SUCCESS (showing first work order):", work_orders[0] if work_orders else "None")
    print(f"Total work orders returned: {len(work_orders)}")
except Exception as e:
    print("FAILED:", e)

# Test 6: get_all_alerts
print("\n6. Testing get_all_alerts():")
try:
    alerts = db_service.get_all_alerts()
    print("SUCCESS (showing first alert):", alerts[0] if alerts else "None")
    print(f"Total alerts returned: {len(alerts)}")
except Exception as e:
    print("FAILED:", e)

# Test 7: get_analytics
print("\n7. Testing get_analytics():")
try:
    analytics = db_service.get_analytics()
    print("SUCCESS:", analytics)
except Exception as e:
    print("FAILED:", e)

# Test 8: create_work_order
print("\n8. Testing create_work_order() for M101:")
try:
    initial_machines = db_service.get_all_machines()
    m101_initial = next(m for m in initial_machines if m["machine_id"] == "M101")
    print("Initial M101 status:", m101_initial)
    
    wo_id = db_service.create_work_order("M101", "High", "Replace bearing B-10 and seal")
    print(f"Work order created with ID: {wo_id}")
    
    updated_machines = db_service.get_all_machines()
    m101_updated = next(m for m in updated_machines if m["machine_id"] == "M101")
    print("Updated M101 status (should be Healthy, failure_probability=0.05):", m101_updated)
except Exception as e:
    print("FAILED:", e)
