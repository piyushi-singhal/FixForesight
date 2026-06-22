from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import random
from datetime import datetime, timedelta

app = FastAPI(title="FixForesight Predictive + Prescriptive Backend")

# Enable CORS for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Contract-Aligned In-Memory database
class MockDB:
    def __init__(self):
        # 1. Machines Directory
        self.machines = {
            "M101": {"machine_id": "M101", "machine_name": "CNC Spindle Unit", "status": "Warning", "temperature": 75.0, "pressure": 30.0, "vibration": 4.8, "rpm": 2500},
            "M102": {"machine_id": "M102", "machine_name": "Hydraulic Press", "status": "Healthy", "temperature": 48.5, "pressure": 120.0, "vibration": 0.8, "rpm": 1200},
            "M103": {"machine_id": "M103", "machine_name": "Injection Molder", "status": "Critical", "temperature": 99.1, "pressure": 85.0, "vibration": 2.1, "rpm": 1800},
            "M104": {"machine_id": "M104", "machine_name": "Robotic Arm Axis 3", "status": "Healthy", "temperature": 35.2, "pressure": 10.0, "vibration": 1.2, "rpm": 900},
            "M105": {"machine_id": "M105", "machine_name": "Cooling Compressor", "status": "Warning", "temperature": 62.4, "pressure": 145.0, "vibration": 3.4, "rpm": 3000}
        }

        # 2. Predictions (TensorFlow model output schema)
        self.predictions = {
            "M101": {"machine_id": "M101", "failure_probability": 82.0, "predicted_failure": "Bearing Failure", "time_to_failure": "5 Days"},
            "M102": {"machine_id": "M102", "failure_probability": 5.0, "predicted_failure": "Normal Operation", "time_to_failure": "N/A"},
            "M103": {"machine_id": "M103", "failure_probability": 94.0, "predicted_failure": "Thermal Overheating", "time_to_failure": "6 Hours"},
            "M104": {"machine_id": "M104", "failure_probability": 12.0, "predicted_failure": "Normal Operation", "time_to_failure": "N/A"},
            "M105": {"machine_id": "M105", "failure_probability": 52.0, "predicted_failure": "Pressure Valve Leak", "time_to_failure": "48 Hours"}
        }

        # 3. Recommendations (Recommendation engine output schema)
        self.recommendations = {
            "M101": {
                "machine_id": "M101",
                "recommendation": "Schedule bearing replacement immediately. Flush grease system and inspect rotor alignment.",
                "priority": "High",
                "confidence": 91.0,
                "required_parts": [{"part_name": "Rotary Bearing B-10", "quantity": 1}, {"part_name": "Hydraulic Pump Seal", "quantity": 2}],
                "estimated_duration_hours": 3.5,
                "created_at": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            "M103": {
                "machine_id": "M103",
                "recommendation": "Perform emergency heat-exchanger cleanout. Replace secondary cooling fan unit and verify coolant pressure.",
                "priority": "Critical",
                "confidence": 96.0,
                "required_parts": [{"part_name": "Cooling Fan F-8", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 1}],
                "estimated_duration_hours": 2.0,
                "created_at": (datetime.now() - timedelta(minutes=45)).isoformat()
            },
            "M105": {
                "machine_id": "M105",
                "recommendation": "Inspect pressure line seal. Replace primary pressure valve V-12 and calibrate limit sensors.",
                "priority": "Medium",
                "confidence": 78.0,
                "required_parts": [{"part_name": "Pressure Valve V-12", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 2}],
                "estimated_duration_hours": 4.0,
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
            }
        }

        # 4. Event Alerts (SNS mock alert feed)
        self.alerts = [
            {"alert_id": 1, "machine_id": "M101", "severity": "Critical", "message": "Bearing failure risk exceeds 80%", "created_at": (datetime.now() - timedelta(hours=4)).isoformat()},
            {"alert_id": 2, "machine_id": "M103", "severity": "Critical", "message": "Machine M103 temperature reached critical levels (99.1°C). Core shutdown initiated.", "created_at": (datetime.now() - timedelta(hours=2)).isoformat()},
            {"alert_id": 3, "machine_id": "M105", "severity": "Warning", "message": "Machine M105 line pressure fluctuated. Recalibration of sensor recommended.", "created_at": (datetime.now() - timedelta(minutes=30)).isoformat()}
        ]

        # 5. Historical Sensor Readings (Sparkline telemetry charts)
        self.sensor_history = {}
        for m_id in ["M101", "M102", "M103", "M104", "M105"]:
            self.sensor_history[m_id] = []
            for i in range(20, 0, -1):
                base_time = datetime.now() - timedelta(minutes=i*2)
                if m_id == "M101":
                    temp = 65.0 + (20 - i) * 0.4
                    vib = 3.0 + (20 - i) * 0.1
                    pres = 28.0 + (i % 3) * 0.2
                elif m_id == "M103":
                    temp = 80.0 + (20 - i) * 0.95
                    vib = 2.0 + (i % 2) * 0.05
                    pres = 80.0 - (20 - i) * 0.2
                elif m_id == "M105":
                    temp = 55.0 + (20 - i) * 0.35
                    vib = 2.0 + (i % 3) * 0.1
                    pres = 135.0 + (20 - i) * 0.5
                else:
                    temp = 45.0 + (i % 4) * 0.1
                    vib = 0.7 + (i % 3) * 0.05
                    pres = 115.0 + (i % 5) * 0.15

                self.sensor_history[m_id].append({
                    "temperature": temp,
                    "vibration": vib,
                    "pressure": pres,
                    "timestamp": base_time.isoformat()
                })

        # 6. Parts Inventory (Used for prescriptive spare check)
        self.parts_inventory = [
            {"part_name": "Rotary Bearing B-10", "quantity": 14, "min_required": 5, "unit_cost": 120.00},
            {"part_name": "High-Temp Gasket G-5", "quantity": 28, "min_required": 10, "unit_cost": 15.50},
            {"part_name": "Pressure Valve V-12", "quantity": 4, "min_required": 3, "unit_cost": 245.00},
            {"part_name": "Hydraulic Pump Seal", "quantity": 3, "min_required": 5, "unit_cost": 45.00},
            {"part_name": "Cooling Fan F-8", "quantity": 19, "min_required": 8, "unit_cost": 35.00},
            {"part_name": "Control Board PCB-9", "quantity": 2, "min_required": 2, "unit_cost": 550.00}
        ]

        # 7. Work Orders
        self.work_orders = [
            {"id": 1, "machine_id": "M101", "status": "completed", "priority": "Medium", "action_required": "Calibrate vibration sensor and tighten mounting bracket bolts.", "created_at": (datetime.now() - timedelta(days=15)).isoformat(), "completed_at": (datetime.now() - timedelta(days=15, hours=2)).isoformat()},
            {"id": 2, "machine_id": "M102", "status": "completed", "priority": "Low", "action_required": "Routine inspection and oil filter replacement.", "created_at": (datetime.now() - timedelta(days=10)).isoformat(), "completed_at": (datetime.now() - timedelta(days=10, hours=1)).isoformat()},
            {"id": 3, "machine_id": "M103", "status": "completed", "priority": "High", "action_required": "Resolved high heat error. Flushed main coolant lines.", "created_at": (datetime.now() - timedelta(days=4)).isoformat(), "completed_at": (datetime.now() - timedelta(days=4, hours=3)).isoformat()},
            {"id": 4, "machine_id": "M101", "status": "in_progress", "priority": "High", "action_required": "Emergency inspection of rotor bearings due to sudden spike in vibration.", "created_at": (datetime.now() - timedelta(hours=4)).isoformat(), "completed_at": None}
        ]

        # 8. Solr Incidents Index
        self.solr_incidents = [
            {"id": "inc-001", "machine_id": "M101", "failure_signature": "Vibration levels spike (bearing wear), high temperature near main drive spindle", "action_taken": "Replaced rotary bearing B-10 and adjusted rotor alignment", "outcome": "Resolved", "date": "2026-03-15T08:00:00Z"},
            {"id": "inc-002", "machine_id": "M103", "failure_signature": "Overheating shutdown triggered, core temperature reached 99.1°C", "action_taken": "Cleaned heat exchanger lines and replaced cooling fan F-8", "outcome": "Resolved", "date": "2026-04-01T14:30:00Z"},
            {"id": "inc-003", "machine_id": "M105", "failure_signature": "Pressure valve leak detected, line pressure fluctuated between 80-140 PSI", "action_taken": "Replaced pressure valve V-12 and high-temp gasket", "outcome": "Resolved", "date": "2026-04-18T11:15:00Z"}
        ]

db = MockDB()

# Models
class WorkOrderRequest(BaseModel):
    machine_id: str
    priority: str
    action_required: str

class AlertWebhookRequest(BaseModel):
    Type: Optional[str] = None
    MessageId: Optional[str] = None
    Subject: Optional[str] = None
    Message: Optional[str] = None
    SubscribeURL: Optional[str] = None

# --- REST Endpoints ---

@app.get("/", response_class=HTMLResponse)
def get_index():
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>FixForesight Front-end File Not Found. Ensure frontend/public/index.html is created.</h1>"

@app.get("/index.html", response_class=HTMLResponse)
def get_index_html():
    return get_index()

@app.get("/health")
def get_health():
    return {
        "status": "healthy",
        "postgres": "healthy (In-Memory FastAPI)",
        "localstack": "healthy",
        "solr": "healthy"
    }

# 1. GET /machines (Contract compliant + fluctuating sensor values)
@app.get("/machines")
def get_machines():
    result = []
    for m_id, m in db.machines.items():
        # Fluctuate telemetry values dynamically
        hist = db.sensor_history.get(m_id, [])
        last = hist[-1] if hist else {"temperature": 50.0, "vibration": 1.0, "pressure": 100.0}
        
        t_fluc = max(30.0, min(140.0, last["temperature"] + random.uniform(-0.4, 0.4)))
        v_fluc = max(0.1, min(25.0, last["vibration"] + random.uniform(-0.08, 0.08)))
        p_fluc = max(10.0, min(250.0, last["pressure"] + random.uniform(-0.5, 0.5)))
        
        last["temperature"] = t_fluc
        last["vibration"] = v_fluc
        last["pressure"] = p_fluc
        
        result.append({
            "machine_id": m["machine_id"],
            "machine_name": m["machine_name"],
            "status": m["status"],
            "temperature": t_fluc,
            "pressure": p_fluc,
            "vibration": v_fluc,
            "rpm": m["rpm"]
        })
    return result

# 2. GET /predictions (Contract compliant)
@app.get("/predictions")
def get_predictions():
    return list(db.predictions.values())

# 3. GET /recommendations (Contract compliant)
@app.get("/recommendations")
def get_recommendations():
    recs = []
    for r_id, r in db.recommendations.items():
        recs.append({
            "machine_id": r["machine_id"],
            "recommendation": r["recommendation"],
            "priority": r["priority"],
            "confidence": r["confidence"]
        })
    return recs

# 4. GET /alerts (Contract compliant)
@app.get("/alerts")
def get_alerts():
    return sorted(db.alerts, key=lambda x: x["created_at"], reverse=True)

# 5. GET /analytics (Contract compliant - dynamic percentages)
@app.get("/analytics")
def get_analytics():
    statuses = [m["status"] for m in db.machines.values()]
    total = len(statuses) or 1
    return {
        "healthy": round((sum(1 for s in statuses if s == "Healthy") / total) * 100),
        "warning": round((sum(1 for s in statuses if s == "Warning") / total) * 100),
        "critical": round((sum(1 for s in statuses if s == "Critical") / total) * 100)
    }

# --- Specific Dashboard Helper Endpoints ---

@app.get("/machines/{machine_id}/risk")
def get_machine_risk(machine_id: str):
    if machine_id not in db.machines:
        raise HTTPException(status_code=404, detail="Machine not found")
    
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

@app.get("/machines/{machine_id}/recommendations")
def get_machine_recommendations(machine_id: str):
    rec = db.recommendations.get(machine_id)
    if not rec:
        return {
            "machine_id": machine_id,
            "has_recommendation": False,
            "message": "No active recommendations. Machine operation normal."
        }
        
    # Check parts stock matching
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

# 6. POST /work-orders (Converts recommendation mitigation, updates stock, resets failure probability)
@app.post("/work-orders")
def create_work_order(req: WorkOrderRequest):
    new_id = len(db.work_orders) + 1
    new_wo = {
        "id": new_id,
        "machine_id": req.machine_id,
        "status": "open",
        "priority": req.priority,
        "action_required": req.action_required,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    db.work_orders.append(new_wo)
    
    # Deduct stock items from parts inventory
    rec = db.recommendations.get(req.machine_id)
    if rec:
        for p in rec["required_parts"]:
            for item in db.parts_inventory:
                if item["part_name"] == p["part_name"]:
                    item["quantity"] = max(0, item["quantity"] - p["quantity"])
                    
        # Reset telemetry failure prediction variables
        db.predictions[req.machine_id]["failure_probability"] = 5.0
        db.predictions[req.machine_id]["predicted_failure"] = "Normal Operation"
        db.predictions[req.machine_id]["time_to_failure"] = "N/A"
        db.machines[req.machine_id]["status"] = "Healthy"
        db.recommendations.pop(req.machine_id, None)
        
    return {"status": "created", "work_order_id": new_id}

# 7. POST /alerts/webhook (Receives SNS alerts)
@app.post("/alerts/webhook")
async def alerts_webhook(req: Request, response: Response):
    body = await req.body()
    try:
        import json
        payload = json.loads(body.decode('utf-8'))
    except Exception:
        payload = {}
        
    msg_type = req.headers.get("x-amz-sns-message-type") or payload.get("Type")
    if msg_type == "SubscriptionConfirmation":
        print(f"SNS Subscription Confirmed: {payload.get('SubscribeURL')}")
        return {"status": "subscription_confirmed"}
        
    new_alert = {
        "alert_id": len(db.alerts) + 1,
        "machine_id": payload.get("Subject", "M101")[-4:] if "M" in payload.get("Subject", "") else "M101",
        "severity": "Critical" if "CRITICAL" in (payload.get("Subject", "")).upper() else "Warning",
        "message": payload.get("Message", str(body)),
        "created_at": datetime.now().isoformat()
    }
    db.alerts.append(new_alert)
    return {"status": "alert_saved"}

# 8. GET /incidents/search (Solr log proxy search helper)
@app.get("/incidents/search")
def search_incidents(q: str = "*:*"):
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
