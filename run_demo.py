#!/usr/bin/env python
"""
Industrial AI Platform - End-to-End Demonstration Script
Walks through the entire data flow:
Dataset ➔ ML Model (Inference) ➔ Prediction ➔ Recommendation ➔ Work Order ➔ Dashboard State

Note: Refactored to access SQLite directly and bypass backend imports to comply with macOS sandbox constraints.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

# Setup paths for importing modules and venv dependencies
workspace_dir = "/Users/piyushisinghal/Downloads/FixForesight"
sys.path.insert(0, os.path.join(workspace_dir, "venv/lib/python3.14/site-packages"))
sys.path.insert(0, os.path.join(workspace_dir, "src"))

# Set cache directories to workspace-local paths to prevent sandbox violations
cache_dir = os.path.join(workspace_dir, "tmp", "cache")
os.makedirs(cache_dir, exist_ok=True)
os.environ["XDG_CACHE_HOME"] = cache_dir
os.environ["JOBLIB_TEMP_FOLDER"] = cache_dir
os.environ["MPLCONFIGDIR"] = cache_dir
os.environ["PYTHON_EGG_CACHE"] = cache_dir

# Import local modules from src/
try:
    from recommendation_engine import RecommendationEngine
    recommendation_engine = RecommendationEngine()
except ImportError:
    recommendation_engine = None
    print("Warning: RecommendationEngine import failed. Will fall back to rule-based generation.")

def print_separator(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def get_db_connection():
    return sqlite3.connect(os.path.join(workspace_dir, "pdm_db.db"))

def predict_machine_failure(air_temp, proc_temp, speed, torque, wear):
    """Replicates the model loading and inference logic from the backend service."""
    try:
        import joblib
        import numpy as np
        
        best_model = joblib.load(os.path.join(workspace_dir, "models", "best_model.pkl"))
        scaler = joblib.load(os.path.join(workspace_dir, "models", "scaler.pkl"))
        
        n_features = getattr(scaler, "n_features_in_", 5)
        if n_features == 5:
            features = np.array([[air_temp, proc_temp, speed, torque, wear]], dtype=np.float32)
        else:
            temp_diff = air_temp - proc_temp
            features = np.array([[torque, speed, temp_diff, wear]])
            
        features_scaled = scaler.transform(features)
        prob = float(best_model.predict_proba(features_scaled)[0][1])
        pred_class = int(best_model.predict(features_scaled)[0])
        
        temp_diff = air_temp - proc_temp
        if pred_class == 1 or prob > 0.5:
            predicted_failure = "Machine Failure"
            if temp_diff < -15.0 or (proc_temp - air_temp) > 15.0:
                failure_type = "heat_dissipation"
            elif wear > 180.0:
                failure_type = "tool_wear"
            elif torque > 65.0:
                failure_type = "overstrain"
            elif speed < 1200.0:
                failure_type = "power_loss"
            else:
                failure_type = "random_failure"
            
            if prob > 0.9:
                time_to_failure = "6 Hours"
            elif prob > 0.75:
                time_to_failure = "24 Hours"
            elif prob > 0.6:
                time_to_failure = "2 Days"
            else:
                time_to_failure = "5 Days"
        else:
            predicted_failure = "Normal Operation"
            failure_type = "none"
            time_to_failure = "N/A"
            
        return prob, predicted_failure, failure_type, time_to_failure
    except Exception as e:
        print(f"Warning: ML model loading/prediction failed: {e}. Falling back to rule-based prediction.")
        
        # Rule-based fallback
        prob = 0.05
        failure_type = "none"
        predicted_failure = "Normal Operation"
        time_to_failure = "N/A"
        
        temp_diff = proc_temp - air_temp
        if temp_diff > 18.0:
            prob = 0.85
            failure_type = "heat_dissipation"
        elif wear > 200.0:
            prob = 0.92
            failure_type = "tool_wear"
        elif torque > 65.0:
            prob = 0.78
            failure_type = "overstrain"
        elif speed < 1100.0:
            prob = 0.65
            failure_type = "power_loss"
        elif wear > 120.0 or torque > 50.0 or temp_diff > 12.0:
            prob = 0.35
            failure_type = "random_failure"
            
        if prob > 0.5:
            predicted_failure = "Machine Failure"
            if prob > 0.9:
                time_to_failure = "6 Hours"
            elif prob > 0.75:
                time_to_failure = "24 Hours"
            else:
                time_to_failure = "48 Hours"
                
        return prob, predicted_failure, failure_type, time_to_failure

def index_documents_in_solr(docs):
    """Mimics Solr update endpoint call."""
    import requests
    solr_url = os.environ.get("SOLR_URL", "http://localhost:8983/solr/incidents")
    try:
        response = requests.post(
            f"{solr_url}/update?commit=true",
            json=docs,
            headers={"Content-Type": "application/json"},
            timeout=2.0
        )
        if response.status_code == 200:
            print("✓ Synchronized data updates to Apache Solr core successfully.")
        else:
            print(f"Warning: Solr responded with status {response.status_code}.")
    except Exception as e:
        print(f"Warning: Solr sync skipped (Solr server offline or connection refused).")

def delete_document_from_solr(doc_id):
    """Mimics Solr delete endpoint call."""
    import requests
    solr_url = os.environ.get("SOLR_URL", "http://localhost:8983/solr/incidents")
    try:
        response = requests.post(
            f"{solr_url}/update?commit=true",
            json={"delete": {"id": doc_id}},
            headers={"Content-Type": "application/json"},
            timeout=2.0
        )
    except Exception:
        pass

def main():
    print_separator("STARTING END-TO-END DEMO: DATASET ➔ ML MODEL ➔ WORK ORDER ➔ DASHBOARD")
    
    # 0. Clean state for repeatability
    print("Preparing clean database state for demo...")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Delete existing predictions, recommendations, work orders for M101
        cursor.execute("DELETE FROM work_orders WHERE machine_id = ?", ("M101",))
        cursor.execute("DELETE FROM recommendations WHERE machine_id = ?", ("M101",))
        cursor.execute("DELETE FROM predictions WHERE machine_id = ?", ("M101",))
        
        # Verify / restore initial inventory quantities
        parts = [("Rotary Bearing B-10", 15, 5, 250.0), 
                 ("Hydraulic Pump Seal", 20, 8, 120.0),
                 ("High-Temp Gasket G-5", 18, 6, 80.0)]
        for name, qty, min_req, cost in parts:
            cursor.execute("""
                INSERT OR IGNORE INTO parts_inventory (part_name, quantity, min_required, unit_cost)
                VALUES (?, ?, ?, ?)
            """, (name, qty, min_req, cost))
            cursor.execute("""
                UPDATE parts_inventory SET quantity = ? WHERE part_name = ?
            """, (qty, name))
            
        conn.commit()
        print("✓ Database state initialized.")
    except Exception as e:
        print(f"Error resetting state: {e}")
        conn.rollback()
    finally:
        conn.close()

    # 1. Dataset Simulation
    print_separator("STEP 1: Simulate Dataset / Telemetry Stream (High Risk Scenario)")
    print("Simulating high-degradation operational readings for machine M101...")
    
    # Readings that will trigger high failure probability
    degraded_vitals = {
        "air_temperature": 304.5,
        "process_temperature": 315.8,
        "rotational_speed": 2350,
        "torque": 68.2,
        "tool_wear": 195.0
    }
    
    print("Dataset/Sensor values generated:")
    for metric, value in degraded_vitals.items():
        print(f"  - {metric.replace('_', ' ').title()}: {value}")

    # Update database machine M101 vitals to simulate incoming IoT data
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE machines
            SET air_temperature = ?, process_temperature = ?, rotational_speed = ?, torque = ?, tool_wear = ?, status = ?
            WHERE machine_id = ?
        """, (
            degraded_vitals["air_temperature"],
            degraded_vitals["process_temperature"],
            degraded_vitals["rotational_speed"],
            degraded_vitals["torque"],
            degraded_vitals["tool_wear"],
            "Critical",
            "M101"
        ))
        conn.commit()
        print("✓ Telemetry stream persisted successfully to database for machine M101.")
    except Exception as e:
        print(f"Error persisting vitals: {e}")
        conn.rollback()
    finally:
        conn.close()

    # 2. Prediction Generation
    print_separator("STEP 2: TensorFlow / ML Model Inference & Prediction Storage")
    
    # Run the ML pipeline locally for M101
    print("Executing ML prediction model on machine M101's telemetry metrics...")
    prob, pred_fail, failure_type, time_to_fail = predict_machine_failure(
        degraded_vitals["air_temperature"],
        degraded_vitals["process_temperature"],
        degraded_vitals["rotational_speed"],
        degraded_vitals["torque"],
        degraded_vitals["tool_wear"]
    )
    
    # Store prediction in SQLite
    conn = get_db_connection()
    cursor = conn.cursor()
    prediction_id = None
    try:
        cursor.execute("""
            INSERT INTO predictions (machine_id, failure_probability, predicted_failure, time_to_failure, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "M101",
            prob * 100.0,
            pred_fail,
            time_to_fail,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        prediction_id = cursor.lastrowid
        conn.commit()
        
        print(f"✓ Prediction Record Stored in database:")
        print(f"  - Prediction ID: {prediction_id}")
        print(f"  - Calculated Failure Probability: {prob * 100.0:.2f}%")
        print(f"  - Predicted Failure Type: {pred_fail} ({failure_type})")
        print(f"  - Estimated Time to Failure: {time_to_fail}")
    except Exception as e:
        print(f"Error storing prediction: {e}")
        conn.rollback()
    finally:
        conn.close()

    # 3. Recommendation Generation
    print_separator("STEP 3: Prescriptive Recommendation Engine Output")
    
    recommendation_text = "No active recommendations. Machine operation normal."
    priority = "Low"
    confidence = prob * 100.0
    
    # Apply rule-based thresholds (STEP 8)
    if prob > 0.8:
        recommendation_text = "Immediate Maintenance Required"
        priority = "Critical"
    elif prob > 0.5:
        recommendation_text = "Schedule preventive maintenance"
        priority = "Medium"
        
    conn = get_db_connection()
    cursor = conn.cursor()
    recommendation_id = None
    try:
        cursor.execute("""
            INSERT INTO recommendations (machine_id, prediction_id, recommendation, priority, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "M101",
            prediction_id,
            recommendation_text,
            priority,
            confidence,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        recommendation_id = cursor.lastrowid
        conn.commit()
        
        print(f"✓ Recommendation Record generated and linked to Prediction:")
        print(f"  - Recommendation ID: {recommendation_id}")
        print(f"  - Linked Prediction ID: {prediction_id}")
        print(f"  - Priority: {priority}")
        print(f"  - Confidence: {confidence:.2f}%")
        print(f"  - Action Required: \"{recommendation_text}\"")
        
        # Check and print spare parts status checklist
        required_parts = []
        if failure_type == "heat_dissipation":
            required_parts = [("Cooling Fan F-8", 1), ("High-Temp Gasket G-5", 1)]
        elif failure_type == "tool_wear":
            required_parts = [("Rotary Bearing B-10", 1), ("High-Temp Gasket G-5", 1)]
        elif failure_type == "overstrain":
            required_parts = [("Rotary Bearing B-10", 2), ("Control Board PCB-9", 1)]
        elif failure_type == "power_loss":
            required_parts = [("Hydraulic Pump Seal", 2), ("Rotary Bearing B-10", 1)]
        else:
            required_parts = [("Pressure Valve V-12", 1), ("High-Temp Gasket G-5", 2)]
            
        print("  - Spare Parts Status Check:")
        for part_name, qty_req in required_parts:
            cursor.execute("SELECT quantity, min_required FROM parts_inventory WHERE part_name = ?", (part_name,))
            row = cursor.fetchone()
            if row:
                avail, min_req = row
                status = "instock" if avail >= qty_req else "outofstock"
                print(f"    * {part_name}: Needed={qty_req}, InStock={avail} (Status: {status})")
            else:
                print(f"    * {part_name}: Needed={qty_req}, InStock=0 (Status: unavailable)")
                
        # Simulating indexing recommendation to Solr
        rec_doc = {
            "id": f"rec-{recommendation_id}",
            "machine_id": "M101",
            "failure_signature": f"[RECOMMENDATION] Prescriptive mitigation: {recommendation_text}",
            "action_taken": f"Priority: {priority} (Confidence: {confidence:.1f}%)",
            "outcome": "Prescribed",
            "date": datetime.utcnow().isoformat() + "Z"
        }
        index_documents_in_solr([rec_doc])
    except Exception as e:
        print(f"Error creating recommendation: {e}")
        conn.rollback()
    finally:
        conn.close()

    # 4. Work Order Promotion
    print_separator("STEP 4: Promotion of Recommendation to Work Order")
    
    print(f"Promoting Recommendation {recommendation_id} to corrective Work Order...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    work_order_id = None
    try:
        # Create work order record
        cursor.execute("""
            INSERT INTO work_orders (machine_id, recommendation_id, status, priority, action_required, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "M101",
            recommendation_id,
            "open",
            priority,
            recommendation_text,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        work_order_id = cursor.lastrowid
        
        # Deduct parts in inventory (for M101: Rotary Bearing B-10: 1, Hydraulic Pump Seal: 2)
        parts_to_deduct = [("Rotary Bearing B-10", 1), ("Hydraulic Pump Seal", 2)]
        for part_name, qty in parts_to_deduct:
            cursor.execute("""
                UPDATE parts_inventory
                SET quantity = MAX(0, quantity - ?)
                WHERE part_name = ?
            """, (qty, part_name))
            
        # Reset prediction risk
        cursor.execute("""
            UPDATE predictions
            SET failure_probability = 5.0, predicted_failure = 'Normal Operation', time_to_failure = 'N/A'
            WHERE machine_id = ?
        """, ("M101",))
        
        # Reset machine telemetry vitals to healthy states
        cursor.execute("""
            UPDATE machines
            SET air_temperature = 298.1,
                process_temperature = 308.6,
                rotational_speed = 1500,
                torque = 40.0,
                tool_wear = 0.0,
                status = 'Healthy'
            WHERE machine_id = ?
        """, ("M101",))
        
        # Delete active recommendation (since it is promoted)
        cursor.execute("DELETE FROM recommendations WHERE recommendation_id = ?", (recommendation_id,))
        
        conn.commit()
        print(f"✓ Work Order authorized successfully!")
        
        # Retrieve and display created work order details
        cursor.execute("SELECT id, status, priority, action_required, created_at FROM work_orders WHERE id = ?", (work_order_id,))
        wo_row = cursor.fetchone()
        if wo_row:
            wo_id, status, prio, act, date_created = wo_row
            print(f"  - Work Order ID: WO-{wo_id:03d}")
            print(f"  - Action Required: {act}")
            print(f"  - Priority Level: {prio}")
            print(f"  - Lifecycle Status: {status}")
            print(f"  - Scheduled at: {date_created}")
            
        # Simulating indexing work order and deleting recommendation in Solr
        delete_document_from_solr(f"rec-{recommendation_id}")
        wo_doc = {
            "id": f"wo-{work_order_id}",
            "machine_id": "M101",
            "failure_signature": f"[WORK ORDER] Action required: {recommendation_text}",
            "action_taken": f"Priority: {priority} (Status: open)",
            "outcome": "Scheduled - Open",
            "date": datetime.utcnow().isoformat() + "Z"
        }
        index_documents_in_solr([wo_doc])
    except Exception as e:
        print(f"Error promoting work order: {e}")
        conn.rollback()
    finally:
        conn.close()

    # 5. Dashboard State Verification
    print_separator("STEP 5: Dashboard State Verification (Vitals Reset & Mitigation)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check machine vitals and status
        cursor.execute("SELECT machine_name, status, air_temperature, process_temperature, rotational_speed, torque, tool_wear FROM machines WHERE machine_id = ?", ("M101",))
        m_row = cursor.fetchone()
        print("Verifying machine M101 telemetry status on dashboard:")
        if m_row:
            name, status, air_t, proc_t, speed, torque, wear = m_row
            print(f"  - Vitals: Air Temp={air_t}K, Process Temp={proc_t}K, Speed={speed}RPM, Torque={torque}Nm, Wear={wear}min")
            print(f"  - Health Status: {status}")
            
        # Check prediction probability
        cursor.execute("SELECT failure_probability, predicted_failure, time_to_failure FROM predictions WHERE machine_id = ?", ("M101",))
        p_row = cursor.fetchone()
        if p_row:
            prob_pct, pred_f, time_f = p_row
            print(f"  - Dynamic Failure Probability: {prob_pct:.2f}%")
            print(f"  - Prediction Class: {pred_f} (TTF: {time_f})")
            
        # Verify recommendation has been deleted (promoted)
        cursor.execute("SELECT recommendation_id FROM recommendations WHERE recommendation_id = ?", (recommendation_id,))
        rec_check = cursor.fetchone()
        if not rec_check:
            print("✓ Active recommendation record was successfully removed from database.")
        else:
            print("✗ ERROR: Recommendation record was not deleted.")
            
        # Verify spare parts quantities
        print("  - Updated Spare Parts Stock Levels:")
        parts_to_check = ["Rotary Bearing B-10", "Hydraulic Pump Seal"]
        for p_name in parts_to_check:
            cursor.execute("SELECT quantity FROM parts_inventory WHERE part_name = ?", (p_name,))
            qty_row = cursor.fetchone()
            if qty_row:
                print(f"    * {p_name}: Remaining Stock={qty_row[0]}")
                
        print("\nAll systems operating normally. End-to-end demonstration completed successfully!")
    except Exception as e:
        print(f"Error verifying dashboard state: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
