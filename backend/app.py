import os
import json
import logging
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

app = FastAPI(title="FixForesight Backend API", version="1.0.0")

# Enable CORS for frontend interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pdm_db")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
SOLR_URL = os.getenv("SOLR_URL", "http://localhost:8983/solr/incidents")

# Detection of mock mode
MOCK_MODE = False
try:
    logger.info("Testing database connection to determine environment...")
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=2)
    conn.close()
    logger.info("Successfully connected to Postgres database. Running in production/DB mode.")
except Exception as e:
    MOCK_MODE = True
    logger.warning("----------------------------------------------------------------------")
    logger.warning("DATABASE CONNECTION FAILED: " + str(e))
    logger.warning("AUTOMATIC FALLBACK TO IN-MEMORY MOCK MODE ACTIVATED!")
    logger.warning("All data, Solr search, and SNS integrations will be simulated in-memory.")
    logger.warning("----------------------------------------------------------------------")

# Models for Request Bodies
class WorkOrderCreate(BaseModel):
    machine_id: int
    priority: str
    action_required: str

class WorkOrderStatusUpdate(BaseModel):
    status: str

# ----------------- In-Memory Mock Store -----------------
class MockStore:
    def __init__(self):
        # 1. Parts Inventory
        self.parts_inventory = [
            {"part_name": "Rotary Bearing B-10", "quantity": 14, "min_required": 5, "unit_cost": 120.00},
            {"part_name": "High-Temp Gasket G-5", "quantity": 28, "min_required": 10, "unit_cost": 15.50},
            {"part_name": "Pressure Valve V-12", "quantity": 4, "min_required": 3, "unit_cost": 245.00},
            {"part_name": "Hydraulic Pump Seal", "quantity": 3, "min_required": 5, "unit_cost": 45.00},
            {"part_name": "Cooling Fan F-8", "quantity": 19, "min_required": 8, "unit_cost": 35.00},
            {"part_name": "Control Board PCB-9", "quantity": 2, "min_required": 2, "unit_cost": 550.00}
        ]

        # 2. Predictions
        self.predictions = {
            1: {"machine_id": 1, "failure_probability": 0.88, "predicted_failure_type": "Bearing Failure", "time_to_failure_hours": 18, "timestamp": datetime.now().isoformat()},
            2: {"machine_id": 2, "failure_probability": 0.05, "predicted_failure_type": "Normal Operation", "time_to_failure_hours": None, "timestamp": datetime.now().isoformat()},
            3: {"machine_id": 3, "failure_probability": 0.94, "predicted_failure_type": "Overheating", "time_to_failure_hours": 6, "timestamp": datetime.now().isoformat()},
            4: {"machine_id": 4, "failure_probability": 0.52, "predicted_failure_type": "Pressure Valve Leak", "time_to_failure_hours": 48, "timestamp": datetime.now().isoformat()},
            5: {"machine_id": 5, "failure_probability": 0.12, "predicted_failure_type": "Slight Mechanical Wear", "time_to_failure_hours": 144, "timestamp": datetime.now().isoformat()}
        }

        # 3. Recommendations
        self.recommendations = {
            1: {
                "id": 101,
                "machine_id": 1,
                "recommended_action": "Schedule bearing replacement immediately. Flush grease system and inspect rotor alignment.",
                "required_parts": [{"part_name": "Rotary Bearing B-10", "quantity": 1}, {"part_name": "Hydraulic Pump Seal", "quantity": 2}],
                "maintenance_priority": "high",
                "estimated_duration_hours": 3.5,
                "created_at": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            3: {
                "id": 103,
                "machine_id": 3,
                "recommended_action": "Perform emergency heat-exchanger cleanout. Replace secondary cooling fan unit and verify coolant pressure.",
                "required_parts": [{"part_name": "Cooling Fan F-8", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 1}],
                "maintenance_priority": "critical",
                "estimated_duration_hours": 2.0,
                "created_at": (datetime.now() - timedelta(minutes=45)).isoformat()
            },
            4: {
                "id": 104,
                "machine_id": 4,
                "recommended_action": "Inspect pressure line seal. Replace primary pressure valve V-12 and calibrate limit sensors.",
                "required_parts": [{"part_name": "Pressure Valve V-12", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 2}],
                "maintenance_priority": "medium",
                "estimated_duration_hours": 4.0,
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
            },
            5: {
                "id": 105,
                "machine_id": 5,
                "recommended_action": "Perform general maintenance at next scheduled downtime. Lubricate linkages and adjust belt tension.",
                "required_parts": [],
                "maintenance_priority": "low",
                "estimated_duration_hours": 1.5,
                "created_at": (datetime.now() - timedelta(hours=4)).isoformat()
            }
        }

        # 4. Work Orders
        self.work_orders = [
            {"id": 1, "machine_id": 1, "status": "completed", "priority": "medium", "action_required": "Calibrate vibration sensor and tighten mounting bracket bolts.", "created_at": (datetime.now() - timedelta(days=15)).isoformat(), "completed_at": (datetime.now() - timedelta(days=15, hours=2)).isoformat()},
            {"id": 2, "machine_id": 2, "status": "completed", "priority": "low", "action_required": "Routine inspection and oil filter replacement.", "created_at": (datetime.now() - timedelta(days=10)).isoformat(), "completed_at": (datetime.now() - timedelta(days=10, hours=1)).isoformat()},
            {"id": 3, "machine_id": 3, "status": "completed", "priority": "high", "action_required": "Resolved high heat error. Flushed main coolant lines.", "created_at": (datetime.now() - timedelta(days=4)).isoformat(), "completed_at": (datetime.now() - timedelta(days=4, hours=3)).isoformat()},
            {"id": 4, "machine_id": 1, "status": "in_progress", "priority": "high", "action_required": "Emergency inspection of rotor bearings due to sudden spike in vibration.", "created_at": (datetime.now() - timedelta(hours=4)).isoformat(), "completed_at": None},
            {"id": 5, "machine_id": 3, "status": "open", "priority": "critical", "action_required": "Perform emergency heat-exchanger cleanout and fan replacement.", "created_at": (datetime.now() - timedelta(hours=1)).isoformat(), "completed_at": None}
        ]

        # 5. Sensor readings history (last 20 logs per machine)
        self.sensor_history = {}
        for m in range(1, 6):
            self.sensor_history[m] = []
            # Seed 20 historical entries
            for i in range(20, 0, -1):
                base_time = datetime.now() - timedelta(minutes=i*2)
                if m == 1:
                    # Vibration climbing
                    temp = 65.0 + (20 - i) * 0.4
                    vib = 3.0 + (20 - i) * 0.3
                    pres = 120.0 + (i % 3) * 0.2
                    err = "W-VIB-01" if i < 5 else None
                elif m == 3:
                    # Temperature climbing
                    temp = 80.0 + (20 - i) * 0.95
                    vib = 2.0 + (i % 2) * 0.05
                    pres = 100.0 - (20 - i) * 0.2
                    err = "E-TEMP-CRIT" if i < 4 else "W-TEMP-HIGH" if i < 10 else None
                elif m == 4:
                    # Pressure climbing
                    temp = 60.0 + (i % 2) * 0.2
                    vib = 2.0 + (i % 3) * 0.1
                    pres = 125.0 + (20 - i) * 0.7
                    err = "W-PRES-HIGH" if i < 6 else None
                else:
                    # Stable values
                    temp = 55.0 + (i % 4) * 0.1
                    vib = 1.2 + (i % 3) * 0.05
                    pres = 115.0 + (i % 5) * 0.15
                    err = None

                self.sensor_history[m].append({
                    "temperature": temp,
                    "vibration": vib,
                    "pressure": pres,
                    "error_code": err,
                    "timestamp": base_time.isoformat()
                })

        # 6. Alerts
        self.alerts = [
            {"id": 1, "message_id": "msg-923847", "subject": "CRITICAL Failure Warning: Machine 3", "message": "Machine 3 is exhibiting critical temperature levels (99.1°C). Core shutdown initiated. Scheduled emergency action required.", "received_at": (datetime.now() - timedelta(hours=2)).isoformat()},
            {"id": 2, "message_id": "msg-923848", "subject": "HIGH Risk Alert: Machine 1", "message": "Machine 1 vibration velocity exceeded safe envelope (8.9 mm/s). High probability of bearing failure. Maintenance order created.", "received_at": (datetime.now() - timedelta(hours=4)).isoformat()}
        ]

        # 7. Solr Historical Incidents cache
        self.solr_incidents = []
        try:
            # Attempt to read incidents from file system
            incidents_path = os.path.join(os.path.dirname(__file__), "..", "infra", "solr", "sample_incidents.json")
            if os.path.exists(incidents_path):
                with open(incidents_path, "r") as f:
                    self.solr_incidents = json.load(f)
                    logger.info(f"Loaded {len(self.solr_incidents)} historical incidents into Mock Solr Cache")
        except Exception as e:
            logger.error(f"Failed to load sample incidents json into mock: {e}")
            # Fallback hardcoded incidents
            self.solr_incidents = [
                {"id": "inc-001", "machine_id": 1, "failure_signature": "Vibration levels spike, bearing failure", "action_taken": "Replaced rotary bearing B-10", "outcome": "Resolved", "date": "2026-03-15T08:00:00Z"},
                {"id": "inc-002", "machine_id": 3, "failure_signature": "Overheating shutdown triggered", "action_taken": "Cleaned heat exchanger and replaced fan F-8", "outcome": "Resolved", "date": "2026-04-01T14:30:00Z"},
                {"id": "inc-003", "machine_id": 4, "failure_signature": "Pressure valve leak detected", "action_taken": "Replaced pressure valve V-12", "outcome": "Resolved", "date": "2026-04-18T11:15:00Z"}
            ]

mock_db = MockStore()

# ----------------- DB / Core Endpoints -----------------

def get_db_connection():
    """Establishes a connection to the PostgreSQL database (Active DB Mode)."""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.get("/health")
def health_check():
    """Verify health of internal components."""
    if MOCK_MODE:
        return {
            "status": "healthy (MOCK MODE)",
            "postgres": "simulated",
            "localstack": "simulated",
            "solr": "simulated",
            "note": "Running in connection-free local mock mode."
        }

    status = {"status": "healthy", "postgres": "healthy", "localstack": "healthy", "solr": "healthy"}
    
    # 1. Test Postgres
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        conn.close()
    except Exception:
        status["postgres"] = "unhealthy"
        status["status"] = "degraded"

    # 2. Test LocalStack
    try:
        response = requests.get(f"{AWS_ENDPOINT_URL}/health", timeout=2)
        if response.status_code != 200:
            status["localstack"] = "unhealthy"
            status["status"] = "degraded"
    except Exception:
        status["localstack"] = "unhealthy"
        status["status"] = "degraded"

    # 3. Test Solr
    try:
        response = requests.get(f"{SOLR_URL}/admin/ping", timeout=2)
        if response.status_code != 200:
            status["solr"] = "unhealthy"
            status["status"] = "degraded"
    except Exception:
        status["solr"] = "unhealthy"
        status["status"] = "degraded"

    return status

@app.get("/machines")
def get_machines():
    """Retrieve overview metrics for all 5 simulated machines."""
    if MOCK_MODE:
        machines_summary = []
        for i in range(1, 6):
            pred = mock_db.predictions.get(i, {"failure_probability": 0.05, "predicted_failure_type": "Normal Operation", "time_to_failure_hours": None})
            history = mock_db.sensor_history.get(i, [])
            last_sensor = history[-1] if history else {"temperature": 50.0, "vibration": 1.0, "pressure": 100.0, "error_code": None}
            
            # Count open orders in mock database
            open_orders = sum(1 for w in mock_db.work_orders if w["machine_id"] == i and w["status"] in ["open", "in_progress"])
            
            # Simulate a small dynamic fluctuate in values to make dashboard live
            import random
            temp_fluc = last_sensor["temperature"] + random.uniform(-0.5, 0.5)
            vib_fluc = last_sensor["vibration"] + random.uniform(-0.1, 0.1)
            pres_fluc = last_sensor["pressure"] + random.uniform(-1.0, 1.0)
            
            # Update history with dynamic fluctuations
            last_sensor["temperature"] = max(30.0, min(150.0, temp_fluc))
            last_sensor["vibration"] = max(0.1, min(20.0, vib_fluc))
            last_sensor["pressure"] = max(50.0, min(250.0, pres_fluc))

            # Simulate spontaneous alerts triggers if temperature or vibration climbs too high
            if i == 1 and last_sensor["vibration"] > 10.0:
                mock_db.predictions[1]["failure_probability"] = 0.95
                mock_db.predictions[1]["time_to_failure_hours"] = 8
            if i == 3 and last_sensor["temperature"] > 100.0:
                mock_db.predictions[3]["failure_probability"] = 0.99
                mock_db.predictions[3]["time_to_failure_hours"] = 2

            machines_summary.append({
                "id": i,
                "name": f"Machine-{i:03d}",
                "failure_probability": pred["failure_probability"],
                "predicted_failure_type": pred["predicted_failure_type"],
                "time_to_failure_hours": pred["time_to_failure_hours"],
                "temperature": last_sensor["temperature"],
                "vibration": last_sensor["vibration"],
                "pressure": last_sensor["pressure"],
                "active_error": last_sensor["error_code"],
                "open_work_orders": open_orders
            })
        return machines_summary

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ON (machine_id) machine_id, failure_probability, predicted_failure_type, time_to_failure_hours, timestamp
                FROM predictions
                ORDER BY machine_id, timestamp DESC;
            """)
            predictions = {p["machine_id"]: p for p in cur.fetchall()}

            cur.execute("""
                SELECT machine_id, COUNT(*) as open_orders 
                FROM work_orders 
                WHERE status IN ('open', 'in_progress') 
                GROUP BY machine_id;
            """)
            work_orders = {w["machine_id"]: w["open_orders"] for w in cur.fetchall()}

            cur.execute("""
                SELECT DISTINCT ON (machine_id) machine_id, temperature, vibration, pressure, error_code
                FROM sensor_readings
                ORDER BY machine_id, timestamp DESC;
            """)
            sensors = {s["machine_id"]: s for s in cur.fetchall()}

        machines_summary = []
        for i in range(1, 6):
            pred = predictions.get(i, {"failure_probability": 0.0, "predicted_failure_type": "Healthy", "time_to_failure_hours": None})
            sens = sensors.get(i, {"temperature": 50.0, "vibration": 1.0, "pressure": 100.0, "error_code": None})
            
            machines_summary.append({
                "id": i,
                "name": f"Machine-{i:03d}",
                "failure_probability": pred["failure_probability"],
                "predicted_failure_type": pred["predicted_failure_type"],
                "time_to_failure_hours": pred["time_to_failure_hours"],
                "temperature": sens["temperature"],
                "vibration": sens["vibration"],
                "pressure": sens["pressure"],
                "active_error": sens["error_code"],
                "open_work_orders": work_orders.get(i, 0)
            })
        return machines_summary
    finally:
        conn.close()

@app.get("/machines/{id}/risk")
def get_machine_risk(id: int):
    """Retrieve detailed failure prediction and historic sensor trend for a machine."""
    if MOCK_MODE:
        if id < 1 or id > 5:
            raise HTTPException(status_code=404, detail="Machine not found")
        pred = mock_db.predictions.get(id, {
            "failure_probability": 0.05,
            "predicted_failure_type": "Normal Operation",
            "time_to_failure_hours": None,
            "timestamp": datetime.now().isoformat()
        })
        history = mock_db.sensor_history.get(id, [])
        return {
            "machine_id": id,
            "prediction": pred,
            "sensor_history": history
        }

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT failure_probability, predicted_failure_type, time_to_failure_hours, timestamp
                FROM predictions
                WHERE machine_id = %s
                ORDER BY timestamp DESC LIMIT 1;
            """, (id,))
            prediction = cur.fetchone()

            cur.execute("""
                SELECT temperature, vibration, pressure, error_code, timestamp
                FROM sensor_readings
                WHERE machine_id = %s
                ORDER BY timestamp DESC LIMIT 20;
            """, (id,))
            readings = cur.fetchall()

        if not prediction:
            prediction = {
                "failure_probability": 0.05,
                "predicted_failure_type": "Normal Operation",
                "time_to_failure_hours": None,
                "timestamp": None
            }

        return {
            "machine_id": id,
            "prediction": prediction,
            "sensor_history": list(reversed(readings))
        }
    finally:
        conn.close()

@app.get("/machines/{id}/recommendations")
def get_machine_recommendations(id: int):
    """Retrieve repair recommendations, checking active inventory stock levels."""
    if MOCK_MODE:
        rec = mock_db.recommendations.get(id)
        if not rec:
            return {
                "machine_id": id,
                "has_recommendation": False,
                "message": "No active recommendations. Machine operation normal."
            }

        inventory_map = {item["part_name"]: item for item in mock_db.parts_inventory}
        parts_list = []
        out_of_stock = False

        for part in rec["required_parts"]:
            name = part["part_name"]
            req_qty = part["quantity"]
            inv = inventory_map.get(name)

            if not inv:
                parts_list.append({
                    "part_name": name,
                    "quantity_required": req_qty,
                    "stock_available": 0,
                    "status": "unavailable",
                    "unit_cost": 0.0
                })
                out_of_stock = True
            else:
                avail = inv["quantity"]
                min_req = inv["min_required"]
                cost = inv["unit_cost"]
                
                if avail >= req_qty:
                    status = "instock" if avail >= min_req else "lowstock"
                else:
                    status = "outofstock"
                    out_of_stock = True

                parts_list.append({
                    "part_name": name,
                    "quantity_required": req_qty,
                    "stock_available": avail,
                    "status": status,
                    "unit_cost": cost
                })

        return {
            "machine_id": id,
            "has_recommendation": True,
            "recommendation_id": rec["id"],
            "recommended_action": rec["recommended_action"],
            "priority": rec["maintenance_priority"],
            "estimated_duration_hours": rec["estimated_duration_hours"],
            "parts_status": parts_list,
            "parts_missing": out_of_stock,
            "created_at": rec["created_at"]
        }

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, recommended_action, required_parts, maintenance_priority, estimated_duration_hours, created_at
                FROM recommendations
                WHERE machine_id = %s
                ORDER BY created_at DESC LIMIT 1;
            """, (id,))
            rec = cur.fetchone()

            cur.execute("SELECT part_name, quantity, min_required, unit_cost FROM parts_inventory;")
            inventory = {item["part_name"]: item for item in cur.fetchall()}

        if not rec:
            return {
                "machine_id": id,
                "has_recommendation": False,
                "message": "No active recommendations. Machine operation normal."
            }

        required_parts = rec["required_parts"]
        parts_list = []
        out_of_stock = False

        for part in required_parts:
            name = part["part_name"]
            req_qty = part["quantity"]
            inv = inventory.get(name)

            if not inv:
                parts_list.append({
                    "part_name": name,
                    "quantity_required": req_qty,
                    "stock_available": 0,
                    "status": "unavailable",
                    "unit_cost": 0.0
                })
                out_of_stock = True
            else:
                avail = inv["quantity"]
                min_req = inv["min_required"]
                cost = inv["unit_cost"]
                
                if avail >= req_qty:
                    status = "instock" if avail >= min_req else "lowstock"
                else:
                    status = "outofstock"
                    out_of_stock = True

                parts_list.append({
                    "part_name": name,
                    "quantity_required": req_qty,
                    "stock_available": avail,
                    "status": status,
                    "unit_cost": cost
                })

        return {
            "machine_id": id,
            "has_recommendation": True,
            "recommendation_id": rec["id"],
            "recommended_action": rec["recommended_action"],
            "priority": rec["maintenance_priority"],
            "estimated_duration_hours": rec["estimated_duration_hours"],
            "parts_status": parts_list,
            "parts_missing": out_of_stock,
            "created_at": rec["created_at"]
        }
    finally:
        conn.close()

@app.get("/alerts")
def get_alerts():
    """Retrieve list of received failure and maintenance alerts."""
    if MOCK_MODE:
        # Return newest first
        return sorted(mock_db.alerts, key=lambda x: x["received_at"], reverse=True)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, message_id, subject, message, received_at FROM alerts ORDER BY received_at DESC LIMIT 50;")
            return cur.fetchall()
    finally:
        conn.close()

@app.post("/alerts/webhook")
async def receive_sns_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook designed to catch, confirm, and store SNS notifications from LocalStack."""
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8")
    
    logger.info(f"SNS Webhook received: {body_str}")
    
    try:
        payload = json.loads(body_str)
    except Exception as e:
        logger.error(f"Failed to parse SNS JSON payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    msg_type = request.headers.get("x-amz-sns-message-type") or payload.get("Type")
    
    if msg_type == "SubscriptionConfirmation":
        subscribe_url = payload.get("SubscribeURL")
        if subscribe_url:
            logger.info(f"Confirming SNS subscription via URL: {subscribe_url}")
            if not MOCK_MODE:
                requests.get(subscribe_url)
            return {"status": "subscription_confirmed"}
        raise HTTPException(status_code=400, detail="Missing SubscribeURL")

    elif msg_type == "Notification":
        msg_id = payload.get("MessageId")
        topic_arn = payload.get("TopicArn")
        subject = payload.get("Subject", "Alert")
        message = payload.get("Message", "")

        if MOCK_MODE:
            new_alert = {
                "id": len(mock_db.alerts) + 1,
                "message_id": msg_id,
                "subject": subject,
                "message": message,
                "received_at": datetime.now().isoformat()
            }
            mock_db.alerts.append(new_alert)
            return {"status": "alert_saved_mock"}

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO alerts (message_id, topic_arn, subject, message) VALUES (%s, %s, %s, %s);",
                    (msg_id, topic_arn, subject, message)
                )
                conn.commit()
            return {"status": "alert_saved"}
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")
            raise HTTPException(status_code=500, detail="Database save failed")
        finally:
            conn.close()

    else:
        # Backup POST support
        subject = payload.get("subject", "System Alert")
        message = payload.get("message", body_str)
        if MOCK_MODE:
            new_alert = {
                "id": len(mock_db.alerts) + 1,
                "message_id": "raw-post",
                "subject": subject,
                "message": message,
                "received_at": datetime.now().isoformat()
            }
            mock_db.alerts.append(new_alert)
            return {"status": "raw_alert_saved_mock"}

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO alerts (message_id, topic_arn, subject, message) VALUES (%s, %s, %s, %s);",
                    ("raw-post", "arn:aws:sns:local", subject, message)
                )
                conn.commit()
            return {"status": "raw_alert_saved"}
        finally:
            conn.close()

@app.get("/incidents/search")
def search_historical_incidents(q: str = "*:*"):
    """Query Apache Solr core for historical incident logs."""
    if MOCK_MODE:
        # Simulate Solr filtering: simple word matches in incidents fields
        results = []
        query_clean = q.lower().strip()
        
        if query_clean == "*:*" or not query_clean:
            results = mock_db.solr_incidents
        else:
            for doc in mock_db.solr_incidents:
                # Search across failure_signature, action_taken, outcome
                text_pool = f"{doc.get('failure_signature', '')} {doc.get('action_taken', '')} {doc.get('outcome', '')} machine-{doc.get('machine_id', '')}".lower()
                if query_clean in text_pool:
                    results.append(doc)
                    
        return {
            "numFound": len(results),
            "docs": results
        }

    try:
        solr_endpoint = f"{SOLR_URL}/select"
        params = {"q": q, "wt": "json", "rows": 20}
        response = requests.get(solr_endpoint, params=params, timeout=5)
        if response.status_code != 200:
            return {"numFound": 0, "docs": []}

        data = response.json()
        resp_data = data.get("response", {})
        return {
            "numFound": resp_data.get("numFound", 0),
            "docs": resp_data.get("docs", [])
        }
    except Exception as e:
        logger.error(f"Solr connection failed: {e}")
        return {"numFound": 0, "docs": [], "error": "Search service unavailable"}

@app.post("/work-orders")
def create_work_order(wo: WorkOrderCreate):
    """Expose endpoint to generate new work orders from recommendations."""
    if MOCK_MODE:
        new_id = len(mock_db.work_orders) + 1
        new_wo = {
            "id": new_id,
            "machine_id": wo.machine_id,
            "status": "open",
            "priority": wo.priority,
            "action_required": wo.action_required,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        mock_db.work_orders.append(new_wo)
        
        # Adjust in-memory parts inventory (deduct recommended parts)
        rec = mock_db.recommendations.get(wo.machine_id)
        if rec:
            for part in rec["required_parts"]:
                name = part["part_name"]
                qty = part["quantity"]
                for inv_item in mock_db.parts_inventory:
                    if inv_item["part_name"] == name:
                        inv_item["quantity"] = max(0, inv_item["quantity"] - qty)

            # Mark prediction/recommendation as completed (reduce probability back to healthy state)
            mock_db.predictions[wo.machine_id]["failure_probability"] = 0.05
            mock_db.predictions[wo.machine_id]["predicted_failure_type"] = "Normal Operation"
            mock_db.predictions[wo.machine_id]["time_to_failure_hours"] = None
            # Remove recommendation since it has been actioned
            mock_db.recommendations.pop(wo.machine_id, None)

        return {"status": "created", "work_order_id": new_id}

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO work_orders (machine_id, status, priority, action_required)
                VALUES (%s, 'open', %s, %s) RETURNING id;
            """, (wo.machine_id, wo.priority, wo.action_required))
            wo_id = cur.fetchone()["id"]
            conn.commit()
        return {"status": "created", "work_order_id": wo_id}
    finally:
        conn.close()

@app.put("/work-orders/{id}")
def update_work_order_status(id: int, status_update: WorkOrderStatusUpdate):
    """Update status of work orders."""
    if MOCK_MODE:
        for wo in mock_db.work_orders:
            if wo["id"] == id:
                wo["status"] = status_update.status
                if status_update.status == "completed":
                    wo["completed_at"] = datetime.now().isoformat()
                return {"status": "updated_mock"}
        raise HTTPException(status_code=404, detail="Work order not found")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if status_update.status == "completed":
                cur.execute("""
                    UPDATE work_orders 
                    SET status = %s, completed_at = CURRENT_TIMESTAMP 
                    WHERE id = %s;
                """, (status_update.status, id))
            else:
                cur.execute("""
                    UPDATE work_orders 
                    SET status = %s 
                    WHERE id = %s;
                """, (status_update.status, id))
            conn.commit()
        return {"status": "updated"}
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    # Local run helper
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
