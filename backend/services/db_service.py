import random
from datetime import datetime, timedelta
from backend.database.connection import db, SessionLocal, SQLAlchemyError
from backend.database import queries
from backend.database.models import Machine, Prediction, Recommendation, Alert, PartInventory, WorkOrder
try:
    from sqlalchemy.orm import Session
except ImportError:
    class DummySession:
        pass
    Session = DummySession

def get_machine_status_helper(status: str) -> str:
    s = status.strip().capitalize()
    if s in ["Healthy", "Warning", "Critical"]:
        return s
    return "Healthy"

def get_all_machines():
    db_sess = SessionLocal()
    try:
        # Check if database is active by querying machines
        db_machines = queries.get_machines(db_sess)
        db_preds = {p.machine_id: p for p in queries.get_predictions(db_sess)}
        db_recs = {r.machine_id: r for r in queries.get_recommendations(db_sess)}
        
        result = []
        for m in db_machines:
            pred = db_preds.get(m.machine_id)
            rec = db_recs.get(m.machine_id)
            
            # predictions has failure_probability in 0.0 to 100.0 (e.g. 82.0), API contract specifies float 0.0 to 1.0 (e.g. 0.82)
            fail_prob = (pred.failure_probability / 100.0) if pred else 0.05
            pred_fail = pred.predicted_failure if pred else "Normal Operation"
            rec_text = rec.recommendation if rec else "No active recommendations. Machine operation normal."
            
            result.append({
                "machine_id": m.machine_id,
                "air_temperature": m.air_temperature,
                "process_temperature": m.process_temperature,
                "rotational_speed": m.rotational_speed,
                "torque": m.torque,
                "tool_wear": m.tool_wear,
                "failure_probability": fail_prob,
                "predicted_failure": pred_fail,
                "recommendation": rec_text
            })
        return result
    except SQLAlchemyError as e:
        # Graceful fallback to MockDB
        result = []
        for m_id, m in db.machines.items():
            hist = db.sensor_history.get(m_id, [])
            last = hist[-1] if hist else {
                "air_temperature": 300.0,
                "process_temperature": 305.0,
                "rotational_speed": 1500,
                "torque": 40.0,
                "tool_wear": 100.0
            }
            
            # Apply slight live telemetry fluctuations for visual interactivity
            at_fluc = max(200.0, min(400.0, last["air_temperature"] + random.uniform(-0.3, 0.3)))
            pt_fluc = max(200.0, min(400.0, last["process_temperature"] + random.uniform(-0.4, 0.4)))
            speed_fluc = max(0, min(5000, int(last["rotational_speed"] + random.uniform(-15, 15))))
            torque_fluc = max(0.0, min(150.0, last["torque"] + random.uniform(-0.5, 0.5)))
            wear_fluc = max(0.0, min(500.0, last["tool_wear"] + random.uniform(0.01, 0.05)))
            
            last["air_temperature"] = at_fluc
            last["process_temperature"] = pt_fluc
            last["rotational_speed"] = speed_fluc
            last["torque"] = torque_fluc
            last["tool_wear"] = wear_fluc
            
            pred = db.predictions.get(m_id, {
                "failure_probability": 5.0,
                "predicted_failure": "Normal Operation"
            })
            rec = db.recommendations.get(m_id, {
                "recommendation": "No active recommendations. Machine operation normal."
            })
            
            result.append({
                "machine_id": m_id,
                "air_temperature": at_fluc,
                "process_temperature": pt_fluc,
                "rotational_speed": speed_fluc,
                "torque": torque_fluc,
                "tool_wear": wear_fluc,
                "failure_probability": float(pred["failure_probability"]) / 100.0,
                "predicted_failure": pred["predicted_failure"],
                "recommendation": rec["recommendation"]
            })
        return result
    finally:
        db_sess.close()

def get_all_predictions():
    db_sess = SessionLocal()
    try:
        # Check database connection
        db_preds = queries.get_predictions(db_sess)
        machines = get_all_machines() # will run on Postgres or fallback automatically
        db_preds_dict = {p.machine_id: p for p in db_preds}
        
        result = []
        for m in machines:
            pred = db_preds_dict.get(m["machine_id"])
            time_to_fail = pred.time_to_failure if pred else "N/A"
            result.append({
                "machine_id": m["machine_id"],
                "air_temperature": m["air_temperature"],
                "process_temperature": m["process_temperature"],
                "rotational_speed": m["rotational_speed"],
                "torque": m["torque"],
                "tool_wear": m["tool_wear"],
                "failure_probability": m["failure_probability"],
                "predicted_failure": m["predicted_failure"],
                "time_to_failure": time_to_fail
            })
        return result
    except SQLAlchemyError as e:
        machines = get_all_machines()
        result = []
        for m in machines:
            pred = db.predictions.get(m["machine_id"], {
                "time_to_failure": "N/A"
            })
            result.append({
                "machine_id": m["machine_id"],
                "air_temperature": m["air_temperature"],
                "process_temperature": m["process_temperature"],
                "rotational_speed": m["rotational_speed"],
                "torque": m["torque"],
                "tool_wear": m["tool_wear"],
                "failure_probability": m["failure_probability"],
                "predicted_failure": m["predicted_failure"],
                "time_to_failure": pred.get("time_to_failure", "N/A")
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
    except SQLAlchemyError as e:
        recs = []
        for r_id, r in db.recommendations.items():
            recs.append({
                "machine_id": r["machine_id"],
                "recommendation": r["recommendation"],
                "priority": r["priority"],
                "confidence": r["confidence"],
                "created_at": r["created_at"]
            })
        return recs
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
    except SQLAlchemyError as e:
        return db.work_orders
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
    except SQLAlchemyError as e:
        return sorted(db.alerts, key=lambda x: x["created_at"], reverse=True)
    finally:
        db_sess.close()

def get_analytics():
    db_sess = SessionLocal()
    try:
        db_machines = queries.get_machines(db_sess)
        statuses = [m.status for m in db_machines]
        total = len(statuses) or 1
        return {
            "healthy": round((sum(1 for s in statuses if get_machine_status_helper(s) == "Healthy") / total) * 100),
            "warning": round((sum(1 for s in statuses if get_machine_status_helper(s) == "Warning") / total) * 100),
            "critical": round((sum(1 for s in statuses if get_machine_status_helper(s) == "Critical") / total) * 100)
        }
    except SQLAlchemyError as e:
        statuses = [m["status"] for m in db.machines.values()]
        total = len(statuses) or 1
        return {
            "healthy": round((sum(1 for s in statuses if s == "Healthy") / total) * 100),
            "warning": round((sum(1 for s in statuses if s == "Warning") / total) * 100),
            "critical": round((sum(1 for s in statuses if s == "Critical") / total) * 100)
        }
    finally:
        db_sess.close()

def get_dashboard_data():
    db_sess = SessionLocal()
    try:
        db_machines = queries.get_machines(db_sess)
        db_alerts = queries.get_alerts(db_sess)
        
        total = len(db_machines)
        healthy = sum(1 for m in db_machines if get_machine_status_helper(m.status) == "Healthy")
        warning = sum(1 for m in db_machines if get_machine_status_helper(m.status) == "Warning")
        critical = sum(1 for m in db_machines if get_machine_status_helper(m.status) == "Critical")
        
        crit_alerts = sum(1 for a in db_alerts if a.severity.lower() in ["critical", "high"])
        
        return {
            "total_machines": total,
            "healthy_machines": healthy,
            "warning_machines": warning,
            "critical_machines": critical,
            "critical_alerts_count": crit_alerts
        }
    except SQLAlchemyError as e:
        statuses = [m["status"] for m in db.machines.values()]
        total = len(statuses)
        healthy = sum(1 for s in statuses if s == "Healthy")
        warning = sum(1 for s in statuses if s == "Warning")
        critical = sum(1 for s in statuses if s == "Critical")
        crit_alerts = sum(1 for a in db.alerts if a["severity"].lower() in ["critical", "high"])
        return {
            "total_machines": total,
            "healthy_machines": healthy,
            "warning_machines": warning,
            "critical_machines": critical,
            "critical_alerts_count": crit_alerts
        }
    finally:
        db_sess.close()

def get_machine_risk(machine_id: str):
    db_sess = SessionLocal()
    try:
        db_m = queries.get_machine(db_sess, machine_id)
        if not db_m:
            return None
        
        pred = db_sess.query(Prediction).filter(Prediction.machine_id == machine_id).first()
        pred_dict = {
            "machine_id": machine_id,
            "failure_probability": pred.failure_probability if pred else 5.0,
            "predicted_failure": pred.predicted_failure if pred else "Normal Operation",
            "time_to_failure": pred.time_to_failure if pred else "N/A"
        }
        
        # fallback telemetry historical readings logic (generated dynamically based on machine characteristics)
        hist = db.sensor_history.get(machine_id, [])
        if len(hist) > 20:
            hist = hist[-20:]
            
        return {
            "machine_id": machine_id,
            "prediction": pred_dict,
            "sensor_history": hist
        }
    except SQLAlchemyError as e:
        if machine_id not in db.machines:
            return None
        pred = db.predictions.get(machine_id, {
            "machine_id": machine_id,
            "failure_probability": 5.0,
            "predicted_failure": "Normal Operation",
            "time_to_failure": "N/A"
        })
        hist = db.sensor_history.get(machine_id, [])
        if len(hist) > 20:
            hist = hist[-20:]
        return {
            "machine_id": machine_id,
            "prediction": pred,
            "sensor_history": hist
        }
    finally:
        db_sess.close()

def get_machine_recommendations(machine_id: str):
    db_sess = SessionLocal()
    try:
        rec = db_sess.query(Recommendation).filter(Recommendation.machine_id == machine_id).first()
        if not rec:
            return {
                "machine_id": machine_id,
                "has_recommendation": False,
                "message": "No active recommendations. Machine operation normal."
            }
            
        # Determine spare parts checklist based on machine ID
        required_parts = []
        if machine_id == "M101":
            required_parts = [{"part_name": "Rotary Bearing B-10", "quantity": 1}, {"part_name": "Hydraulic Pump Seal", "quantity": 2}]
        elif machine_id == "M103":
            required_parts = [{"part_name": "Cooling Fan F-8", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 1}]
        elif machine_id == "M105":
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
                
        return {
            "machine_id": machine_id,
            "has_recommendation": True,
            "recommendation": rec.recommendation,
            "priority": rec.priority,
            "confidence": rec.confidence,
            "parts_status": parts_status,
            "parts_missing": out_of_stock,
            "estimated_duration_hours": 3.5 if machine_id == "M101" else 2.0 if machine_id == "M103" else 4.0,
            "created_at": rec.created_at.isoformat() if isinstance(rec.created_at, datetime) else str(rec.created_at)
        }
    except SQLAlchemyError as e:
        rec = db.recommendations.get(machine_id)
        if not rec:
            return {
                "machine_id": machine_id,
                "has_recommendation": False,
                "message": "No active recommendations. Machine operation normal."
            }
            
        parts_status = []
        out_of_stock = False
        for p in rec["required_parts"]:
            inv_item = next((item for item in db.parts_inventory if item["part_name"] == p["part_name"]), None)
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
                avail = inv_item["quantity"]
                min_req = inv_item["min_required"]
                
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
                    "unit_cost": inv_item["unit_cost"]
                })
                
        return {
            "machine_id": machine_id,
            "has_recommendation": True,
            "recommendation": rec["recommendation"],
            "priority": rec["priority"],
            "confidence": rec["confidence"],
            "parts_status": parts_status,
            "parts_missing": out_of_stock,
            "estimated_duration_hours": rec["estimated_duration_hours"],
            "created_at": rec["created_at"]
        }
    finally:
        db_sess.close()

def create_work_order(machine_id: str, priority: str, action_required: str):
    db_sess = SessionLocal()
    try:
        # Create database work order
        db_wo = WorkOrder(
            machine_id=machine_id,
            status="open",
            priority=priority,
            action_required=action_required,
            created_at=datetime.utcnow()
        )
        db_sess.add(db_wo)
        
        # Mappings of standard parts based on recommendation
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
                
        # Reset prediction failure risk
        pred = db_sess.query(Prediction).filter(Prediction.machine_id == machine_id).first()
        if pred:
            pred.failure_probability = 5.0
            pred.predicted_failure = "Normal Operation"
            pred.time_to_failure = "N/A"
            
        # Update machine status
        machine = db_sess.query(Machine).filter(Machine.machine_id == machine_id).first()
        if machine:
            machine.status = "Healthy"
            
        # Remove recommendation
        rec = db_sess.query(Recommendation).filter(Recommendation.machine_id == machine_id).first()
        if rec:
            db_sess.delete(rec)
            
        db_sess.commit()
        db_sess.refresh(db_wo)
        return db_wo.id
    except SQLAlchemyError as e:
        new_id = len(db.work_orders) + 1
        new_wo = {
            "id": new_id,
            "machine_id": machine_id,
            "status": "open",
            "priority": priority,
            "action_required": action_required,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        db.work_orders.append(new_wo)
        
        rec = db.recommendations.get(machine_id)
        if rec:
            for p in rec["required_parts"]:
                for item in db.parts_inventory:
                    if item["part_name"] == p["part_name"]:
                        item["quantity"] = max(0, item["quantity"] - p["quantity"])
                        
            db.predictions[machine_id]["failure_probability"] = 5.0
            db.predictions[machine_id]["predicted_failure"] = "Normal Operation"
            db.predictions[machine_id]["time_to_failure"] = "N/A"
            db.machines[machine_id]["status"] = "Healthy"
            db.recommendations.pop(machine_id, None)
            
        return new_id
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
    except SQLAlchemyError as e:
        new_id = len(db.alerts) + 1
        new_alert = {
            "alert_id": new_id,
            "machine_id": machine_id,
            "severity": severity,
            "message": message,
            "created_at": datetime.now().isoformat()
        }
        db.alerts.append(new_alert)
        return new_id
    finally:
        db_sess.close()

def search_incidents(q: str):
    # Solr historical query remains fully functional
    query_clean = q.lower().strip()
    results = []
    if query_clean == "*:*" or not query_clean:
        results = db.solr_incidents
    else:
        for doc in db.solr_incidents:
            text_pool = f"{doc.get('failure_signature', '')} {doc.get('action_taken', '')} {doc.get('outcome', '')} {doc.get('machine_id', '')}".lower()
            if query_clean in text_pool:
                results.append(doc)
    return {
        "numFound": len(results),
        "docs": results
    }
