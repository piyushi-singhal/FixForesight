import random
from datetime import datetime, timedelta
import sys
import os
from src.backend_copy.database.connection import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from src.backend_copy.database import queries
from src.backend_copy.database.models import Machine, Prediction, Recommendation, Alert, PartInventory, WorkOrder

try:
    from sqlalchemy.orm import Session
except ImportError:
    class DummySession:
        pass
    Session = DummySession

# Add root/src to path for dynamic imports
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(base_dir, "src"))

try:
    from recommendation_engine import RecommendationEngine
    recommendation_engine = RecommendationEngine()
except ImportError:
    recommendation_engine = None

MODEL_AVAILABLE = False
best_model = None
scaler = None
IS_KERAS_MODEL = False

try:
    import joblib
    import numpy as np
    
    keras_model_path = os.path.join(base_dir, "models", "best_model.h5")
    pkl_model_path = os.path.join(base_dir, "models", "best_model.pkl")
    scaler_path = os.path.join(base_dir, "models", "scaler.pkl")
    
    # Try loading Keras model first if tensorflow is installed
    if os.path.exists(keras_model_path) and os.path.exists(scaler_path):
        try:
            import tensorflow as tf
            best_model = tf.keras.models.load_model(keras_model_path)
            scaler = joblib.load(scaler_path)
            MODEL_AVAILABLE = True
            IS_KERAS_MODEL = True
            print("✓ Successfully loaded Keras model and scaler")
        except Exception as keras_err:
            print(f"Warning: Failed to load Keras model ({keras_err}). Falling back to PKL.")
            
    # Fallback to PKL if Keras load failed or is not available
    if not MODEL_AVAILABLE and os.path.exists(pkl_model_path) and os.path.exists(scaler_path):
        best_model = joblib.load(pkl_model_path)
        scaler = joblib.load(scaler_path)
        MODEL_AVAILABLE = True
        IS_KERAS_MODEL = False
        print("✓ Successfully loaded scikit-learn model and scaler")
except Exception as e:
    print(f"Warning: ML model loading failed: {e}. Falling back to rule-based prediction.")

def predict_machine_failure(air_temp, proc_temp, speed, torque, wear):
    if MODEL_AVAILABLE and best_model is not None and scaler is not None:
        try:
            if IS_KERAS_MODEL:
                # Features for Keras: ['air_temperature', 'process_temperature', 'rotational_speed', 'torque', 'tool_wear']
                features = np.array([[air_temp, proc_temp, speed, torque, wear]], dtype=np.float32)
                
                # Scale features
                features_scaled = scaler.transform(features)
                
                # Predict probability using Keras Sequential model
                prob = float(best_model.predict(features_scaled, verbose=0)[0][0])
                
                # Predict class
                pred_class = int(prob > 0.5)
            else:
                # Fallback scikit-learn logic
                n_features = getattr(scaler, "n_features_in_", 4)
                if n_features == 5:
                    features = np.array([[air_temp, proc_temp, speed, torque, wear]], dtype=np.float32)
                else:
                    # 4 features fallback: ['Torque [Nm]', 'Rotational speed [rpm]', 'temp_difference', 'Tool wear [min]']
                    temp_diff = air_temp - proc_temp
                    features = np.array([[torque, speed, temp_diff, wear]])
                    
                # Scale features
                features_scaled = scaler.transform(features)
                
                # Predict probability
                prob = float(best_model.predict_proba(features_scaled)[0][1])
                
                # Predict class
                pred_class = int(best_model.predict(features_scaled)[0])
            
            # Determine failure type and time to failure
            temp_diff = air_temp - proc_temp
            if pred_class == 1 or prob > 0.5:
                predicted_failure = "Machine Failure"
                # Determine failure mode based on simulator logic
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
                
                # Estimate time to failure based on probability
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
            pass
            
    # Rule-based fallback if model is not available or errors out
    prob = 0.05
    failure_type = "none"
    predicted_failure = "Normal Operation"
    time_to_failure = "N/A"
    
    # Check thresholds
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

def get_machine_status_helper(status: str) -> str:
    s = status.strip().capitalize()
    if s in ["Healthy", "Warning", "Critical"]:
        return s
    return "Healthy"

def get_all_machines():
    db_sess = SessionLocal()
    try:
        db_machines = queries.get_machines(db_sess)
        
        result = []
        for m in db_machines:
            prob, pred_fail, failure_type, time_to_fail = predict_machine_failure(
                m.air_temperature, m.process_temperature, m.rotational_speed, m.torque, m.tool_wear
            )
            
            rec_text = "No active recommendations. Machine operation normal."
            if prob > 0.5 and recommendation_engine:
                rec_obj = recommendation_engine.generate_recommendation(
                    machine_id=int(m.machine_id.replace("M", "") or 1) if isinstance(m.machine_id, str) else m.machine_id,
                    prediction_id=0,
                    failure_type=failure_type,
                    failure_probability=prob
                )
                rec_text = rec_obj.action.replace("• ", "").replace("\n", "; ")
            
            result.append({
                "machine_id": m.machine_id,
                "air_temperature": m.air_temperature,
                "process_temperature": m.process_temperature,
                "rotational_speed": m.rotational_speed,
                "torque": m.torque,
                "tool_wear": m.tool_wear,
                "failure_probability": prob,
                "predicted_failure": pred_fail,
                "recommendation": rec_text
            })
        return result
    finally:
        db_sess.close()

def get_all_predictions():
    db_sess = SessionLocal()
    try:
        db_preds = queries.get_predictions(db_sess)
        result = []
        for p in db_preds:
            m = p.machine
            result.append({
                "machine_id": p.machine_id,
                "air_temperature": m.air_temperature if m else 0.0,
                "process_temperature": m.process_temperature if m else 0.0,
                "rotational_speed": m.rotational_speed if m else 0,
                "torque": m.torque if m else 0.0,
                "tool_wear": m.tool_wear if m else 0.0,
                "failure_probability": p.failure_probability,
                "predicted_failure": p.predicted_failure,
                "time_to_failure": p.time_to_failure
            })
        return result
    finally:
        db_sess.close()

def get_all_recommendations():
    db_sess = SessionLocal()
    try:
        db_recs = queries.get_recommendations(db_sess)
        return [
            {
                "machine_id": r.machine_id,
                "recommendation": r.recommendation,
                "priority": r.priority,
                "confidence": r.confidence,
                "created_at": r.created_at.isoformat() if isinstance(r.created_at, datetime) else str(r.created_at)
            } for r in db_recs
        ]
    finally:
        db_sess.close()

def get_all_work_orders():
    db_sess = SessionLocal()
    try:
        db_wos = queries.get_work_orders(db_sess)
        return [
            {
                "id": w.id,
                "machine_id": w.machine_id,
                "status": w.status,
                "priority": w.priority,
                "action_required": w.action_required,
                "created_at": w.created_at.isoformat() if isinstance(w.created_at, datetime) else str(w.created_at),
                "completed_at": w.completed_at.isoformat() if w.completed_at else None
            } for w in db_wos
        ]
    finally:
        db_sess.close()

def get_all_alerts():
    db_sess = SessionLocal()
    try:
        db_alerts = queries.get_alerts(db_sess)
        return [
            {
                "alert_id": a.alert_id,
                "machine_id": a.machine_id,
                "severity": a.severity,
                "message": a.message,
                "created_at": a.created_at.isoformat() if isinstance(a.created_at, datetime) else str(a.created_at)
            } for a in db_alerts
        ]
    finally:
        db_sess.close()

def get_analytics():
    db_sess = SessionLocal()
    try:
        from src.backend_copy.database.models import Machine, WorkOrder
        db_machines = db_sess.query(Machine).all()
        
        healthy_count = 0
        warning_count = 0
        critical_count = 0
        
        for m in db_machines:
            prob, pred_fail, failure_type, time_to_fail = predict_machine_failure(
                m.air_temperature, m.process_temperature, m.rotational_speed, m.torque, m.tool_wear
            )
            if prob <= 0.4:
                healthy_count += 1
            elif prob <= 0.8:
                warning_count += 1
            else:
                critical_count += 1
                
        total = len(db_machines) or 1
        
        open_wos = db_sess.query(WorkOrder).filter(WorkOrder.status != "completed").count()
        completed_wos = db_sess.query(WorkOrder).filter(WorkOrder.status == "completed").count()
        
        return {
            "healthy": round((healthy_count / total) * 100),
            "warning": round((warning_count / total) * 100),
            "critical": round((critical_count / total) * 100),
            "healthy_machines": healthy_count,
            "warning_machines": warning_count,
            "critical_machines": critical_count,
            "open_work_orders": open_wos,
            "completed_work_orders": completed_wos
        }
    finally:
        db_sess.close()

def get_dashboard_data():
    machines = get_all_machines()
    total = len(machines)
    healthy = sum(1 for m in machines if m["failure_probability"] <= 0.4)
    warning = sum(1 for m in machines if 0.4 < m["failure_probability"] <= 0.8)
    critical = sum(1 for m in machines if m["failure_probability"] > 0.8)
    crit_alerts = sum(1 for m in machines if m["failure_probability"] > 0.8)
    return {
        "total_machines": total,
        "healthy_machines": healthy,
        "warning_machines": warning,
        "critical_machines": critical,
        "critical_alerts_count": crit_alerts
    }

def get_machine_risk(machine_id: str):
    db_sess = SessionLocal()
    try:
        db_m = queries.get_machine(db_sess, machine_id)
        if not db_m:
            return None
        
        prob, pred_fail, failure_type, time_to_fail = predict_machine_failure(
            db_m.air_temperature, db_m.process_temperature, db_m.rotational_speed, db_m.torque, db_m.tool_wear
        )
        
        pred_dict = {
            "machine_id": machine_id,
            "failure_probability": prob * 100.0,
            "predicted_failure": pred_fail,
            "time_to_failure": time_to_fail
        }
        
        hist = []
        for i in range(20, 0, -1):
            base_time = datetime.now() - timedelta(minutes=i*2)
            factor = (20 - i) / 20.0
            hist.append({
                "air_temperature": db_m.air_temperature - (1.0 - factor) * 2.0 + random.uniform(-0.1, 0.1),
                "process_temperature": db_m.process_temperature - (1.0 - factor) * 2.5 + random.uniform(-0.1, 0.1),
                "rotational_speed": int(db_m.rotational_speed - (1.0 - factor) * 100 + random.uniform(-10, 10)),
                "torque": db_m.torque - (1.0 - factor) * 3.0 + random.uniform(-0.2, 0.2),
                "tool_wear": max(0.0, db_m.tool_wear - (20 - i) * 0.5),
                "timestamp": base_time.isoformat()
            })
            
        return {
            "machine_id": machine_id,
            "prediction": pred_dict,
            "sensor_history": hist
        }
    finally:
        db_sess.close()

def get_machine_recommendations(machine_id: str):
    db_sess = SessionLocal()
    try:
        db_m = queries.get_machine(db_sess, machine_id)
        if not db_m:
            return {
                "machine_id": machine_id,
                "has_recommendation": False,
                "message": "No active recommendations. Machine operation normal."
            }
        
        prob, pred_fail, failure_type, time_to_fail = predict_machine_failure(
            db_m.air_temperature, db_m.process_temperature, db_m.rotational_speed, db_m.torque, db_m.tool_wear
        )
        
        if prob <= 0.5:
            return {
                "machine_id": machine_id,
                "has_recommendation": False,
                "message": "No active recommendations. Machine operation normal."
            }
            
        rec_obj = None
        if recommendation_engine:
            rec_obj = recommendation_engine.generate_recommendation(
                machine_id=int(machine_id.replace("M", "") or 1) if isinstance(machine_id, str) else machine_id,
                prediction_id=0,
                failure_type=failure_type,
                failure_probability=prob
            )
            
        required_parts = []
        if failure_type == "heat_dissipation":
            required_parts = [{"part_name": "Cooling Fan F-8", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 1}]
        elif failure_type == "tool_wear":
            required_parts = [{"part_name": "Rotary Bearing B-10", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 1}]
        elif failure_type == "overstrain":
            required_parts = [{"part_name": "Rotary Bearing B-10", "quantity": 2}, {"part_name": "Control Board PCB-9", "quantity": 1}]
        elif failure_type == "power_loss":
            required_parts = [{"part_name": "Hydraulic Pump Seal", "quantity": 2}, {"part_name": "Rotary Bearing B-10", "quantity": 1}]
        else:
            required_parts = [{"part_name": "Pressure Valve V-12", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 2}]
            
        parts_status = []
        out_of_stock = False
        for p in required_parts:
            inv_item = db_sess.query(PartInventory).filter(PartInventory.part_name == p["part_name"]).first()
            if not inv_item:
                parts_status.append({
                    "part_name": p["part_name"],
                    "quantity_required": p["quantity"],
                    "stock_available": 0,
                    "status": "unavailable",
                    "unit_cost": 0.0
                })
                out_of_stock = True
            else:
                avail = inv_item.quantity
                min_req = inv_item.min_required
                
                if avail >= p["quantity"]:
                    status = "instock" if avail >= min_req else "lowstock"
                else:
                    status = "outofstock"
                    out_of_stock = True
                    
                parts_status.append({
                    "part_name": p["part_name"],
                    "quantity_required": p["quantity"],
                    "stock_available": avail,
                    "status": status,
                    "unit_cost": inv_item.unit_cost
                })
                
        rec_text = rec_obj.action.replace("• ", "").replace("\n", "; ") if rec_obj else "Schedule preventive maintenance"
        priority = rec_obj.priority if rec_obj else "medium"
        confidence = float(rec_obj.failure_probability * 100.0) if rec_obj else (prob * 100.0)
        return {
            "machine_id": machine_id,
            "has_recommendation": True,
            "recommendation": rec_text,
            "priority": priority.capitalize(),
            "confidence": confidence,
            "parts_status": parts_status,
            "parts_missing": out_of_stock,
            "estimated_duration_hours": rec_obj.estimated_cost / 150.0 if rec_obj else 3.0,
            "created_at": datetime.now().isoformat()
        }
    finally:
        db_sess.close()

def create_work_order(machine_id: str, priority: str, action_required: str):
    db_sess = SessionLocal()
    try:
        db_wo = WorkOrder(
            machine_id=machine_id,
            status="open",
            priority=priority,
            action_required=action_required,
            created_at=datetime.utcnow()
        )
        db_sess.add(db_wo)
        
        parts_to_deduct = []
        if machine_id == "M101":
            parts_to_deduct = [("Rotary Bearing B-10", 1), ("Hydraulic Pump Seal", 2)]
        elif machine_id == "M103":
            parts_to_deduct = [("Cooling Fan F-8", 1), ("High-Temp Gasket G-5", 1)]
        elif machine_id == "M105":
            parts_to_deduct = [("Pressure Valve V-12", 1), ("High-Temp Gasket G-5", 2)]
            
        for p_name, qty in parts_to_deduct:
            part = db_sess.query(PartInventory).filter(PartInventory.part_name == p_name).first()
            if part:
                part.quantity = max(0, part.quantity - qty)
                
        pred = db_sess.query(Prediction).filter(Prediction.machine_id == machine_id).first()
        if pred:
            pred.failure_probability = 5.0
            pred.predicted_failure = "Normal Operation"
            pred.time_to_failure = "N/A"
            
        machine = db_sess.query(Machine).filter(Machine.machine_id == machine_id).first()
        if machine:
            machine.status = "Healthy"
            
        rec = db_sess.query(Recommendation).filter(Recommendation.machine_id == machine_id).first()
        if rec:
            db_sess.delete(rec)
            
        db_sess.commit()
        db_sess.refresh(db_wo)
        return db_wo.id
    finally:
        db_sess.close()

def create_raw_alert(machine_id: str, severity: str, message: str):
    db_sess = SessionLocal()
    try:
        db_alert = Alert(
            machine_id=machine_id,
            severity=severity,
            message=message,
            created_at=datetime.utcnow()
        )
        db_sess.add(db_alert)
        db_sess.commit()
        db_sess.refresh(db_alert)
        return db_alert.alert_id
    finally:
        db_sess.close()

def search_incidents(q: str):
    import requests
    solr_url = os.environ.get("SOLR_URL", "http://localhost:8983/solr/incidents")
    
    static_incidents = [
        {"id": "inc-001", "machine_id": "M101", "failure_signature": "Vibration levels spike (bearing wear), high temperature near main drive spindle", "action_taken": "Replaced rotary bearing B-10 and adjusted rotor alignment", "outcome": "Resolved", "date": "2026-03-15T08:00:00Z"},
        {"id": "inc-002", "machine_id": "M103", "failure_signature": "Overheating shutdown triggered, core temperature reached 99.1°C", "action_taken": "Cleaned heat exchanger lines and replaced cooling fan F-8", "outcome": "Resolved", "date": "2026-04-01T14:30:00Z"},
        {"id": "inc-003", "machine_id": "M105", "failure_signature": "Pressure valve leak detected, line pressure fluctuated between 80-140 PSI", "action_taken": "Replaced pressure valve V-12 and high-temp gasket", "outcome": "Resolved", "date": "2026-04-18T11:15:00Z"}
    ]
    
    try:
        query_clean = q.strip() if q else ""
        if not query_clean or query_clean == "*:*":
            solr_query = "*:*"
        else:
            solr_query = f"failure_signature:*{query_clean}* OR action_taken:*{query_clean}* OR outcome:*{query_clean}* OR machine_id:*{query_clean}*"
            
        response = requests.get(
            f"{solr_url}/select",
            params={"q": solr_query, "wt": "json", "rows": 100},
            timeout=3.0
        )
        if response.status_code == 200:
            data = response.json()
            response_data = data.get("response", {})
            return {
                "numFound": response_data.get("numFound", 0),
                "docs": response_data.get("docs", [])
            }
    except Exception as e:
        print(f"Warning: Solr request failed ({e}). Falling back to local static search.")
        
    query_clean = q.lower().strip() if q else ""
    results = []
    if query_clean == "*:*" or not query_clean:
        results = static_incidents
    else:
        for doc in static_incidents:
            text_pool = f"{doc.get('failure_signature', '')} {doc.get('action_taken', '')} {doc.get('outcome', '')} {doc.get('machine_id', '')}".lower()
            if query_clean in text_pool:
                results.append(doc)
    return {
        "numFound": len(results),
        "docs": results
    }
