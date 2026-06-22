import random
from datetime import datetime
from backend.database.connection import db

def get_all_machines():
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
        
        # Look up mock predictions and recommendations
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

def get_all_predictions():
    return list(db.predictions.values())

def get_all_recommendations():
    recs = []
    for r_id, r in db.recommendations.items():
        recs.append({
            "machine_id": r["machine_id"],
            "recommendation": r["recommendation"],
            "priority": r["priority"],
            "confidence": r["confidence"]
        })
    return recs

def get_all_alerts():
    return sorted(db.alerts, key=lambda x: x["created_at"], reverse=True)

def get_analytics():
    statuses = [m["status"] for m in db.machines.values()]
    total = len(statuses) or 1
    return {
        "healthy": round((sum(1 for s in statuses if s == "Healthy") / total) * 100),
        "warning": round((sum(1 for s in statuses if s == "Warning") / total) * 100),
        "critical": round((sum(1 for s in statuses if s == "Critical") / total) * 100)
    }

def get_machine_risk(machine_id: str):
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

def get_machine_recommendations(machine_id: str):
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

def create_work_order(machine_id: str, priority: str, action_required: str):
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

def create_raw_alert(machine_id: str, severity: str, message: str):
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

def search_incidents(q: str):
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
