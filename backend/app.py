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

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

app = FastAPI(title="FixForesight Backend API", version="1.0.0")

# Enable CORS for frontend interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify front-end origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/pdm_db")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
SOLR_URL = os.getenv("SOLR_URL", "http://solr:8983/solr/incidents")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Models for Request Bodies
class WorkOrderCreate(BaseModel):
    machine_id: int
    priority: str
    action_required: str

class WorkOrderStatusUpdate(BaseModel):
    status: str

@app.get("/health")
def health_check():
    """Verify health of internal components: Postgres, LocalStack, and Solr."""
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

    if status["status"] == "degraded":
        return status
    return status

@app.get("/machines")
def get_machines():
    """Retrieve overview metrics for all 5 simulated machines."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get latest prediction for all machines
            cur.execute("""
                SELECT DISTINCT ON (machine_id) machine_id, failure_probability, predicted_failure_type, time_to_failure_hours, timestamp
                FROM predictions
                ORDER BY machine_id, timestamp DESC;
            """)
            predictions = {p["machine_id"]: p for p in cur.fetchall()}

            # Get active work order counts
            cur.execute("""
                SELECT machine_id, COUNT(*) as open_orders 
                FROM work_orders 
                WHERE status IN ('open', 'in_progress') 
                GROUP BY machine_id;
            """)
            work_orders = {w["machine_id"]: w["open_orders"] for w in cur.fetchall()}

            # Get latest sensor reading parameters
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
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Fetch latest prediction
            cur.execute("""
                SELECT failure_probability, predicted_failure_type, time_to_failure_hours, timestamp
                FROM predictions
                WHERE machine_id = %s
                ORDER BY timestamp DESC LIMIT 1;
            """, (id,))
            prediction = cur.fetchone()

            # 2. Fetch recent sensor trends (last 20 readings)
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
            "sensor_history": list(reversed(readings))  # Chronological order
        }
    finally:
        conn.close()

@app.get("/machines/{id}/recommendations")
def get_machine_recommendations(id: int):
    """Retrieve repair recommendations, checking active inventory stock levels."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Fetch latest recommendation
            cur.execute("""
                SELECT id, recommended_action, required_parts, maintenance_priority, estimated_duration_hours, created_at
                FROM recommendations
                WHERE machine_id = %s
                ORDER BY created_at DESC LIMIT 1;
            """, (id,))
            rec = cur.fetchone()

            # 2. Fetch inventory values to check stock
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
                # Part not cataloged
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
                
                # Check stock status
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
    
    # Log incoming request headers and payload
    logger.info(f"SNS Webhook received payload: {body_str}")
    
    try:
        payload = json.loads(body_str)
    except Exception as e:
        logger.error(f"Failed to parse SNS JSON payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # AWS/LocalStack Subscription Confirmation handling
    msg_type = request.headers.get("x-amz-sns-message-type") or payload.get("Type")
    
    if msg_type == "SubscriptionConfirmation":
        subscribe_url = payload.get("SubscribeURL")
        if subscribe_url:
            logger.info(f"Confirming SNS subscription via URL: {subscribe_url}")
            # Run confirmations asynchronously or inline
            requests.get(subscribe_url)
            return {"status": "subscription_confirmed"}
        raise HTTPException(status_code=400, detail="Missing SubscribeURL")

    elif msg_type == "Notification":
        # Handle regular SNS notification message
        msg_id = payload.get("MessageId")
        topic_arn = payload.get("TopicArn")
        subject = payload.get("Subject", "Alert")
        message = payload.get("Message", "")

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO alerts (message_id, topic_arn, subject, message) VALUES (%s, %s, %s, %s);",
                    (msg_id, topic_arn, subject, message)
                )
                conn.commit()
            logger.info(f"SNS alert {msg_id} saved to database")
            return {"status": "alert_saved"}
        except Exception as e:
            logger.error(f"Failed to save alert to DB: {e}")
            raise HTTPException(status_code=500, detail="Database save failed")
        finally:
            conn.close()

    # Raw POST payload backup support (for sensor-simulator testing)
    else:
        subject = payload.get("subject", "System Alert")
        message = payload.get("message", body_str)
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
    try:
        solr_endpoint = f"{SOLR_URL}/select"
        # Forward query parameters to Solr
        params = {
            "q": q,
            "wt": "json",
            "rows": 20
        }
        logger.info(f"Proxying query to Solr: {solr_endpoint} with params {params}")
        response = requests.get(solr_endpoint, params=params, timeout=5)
        
        if response.status_code != 200:
            logger.error(f"Solr search failed with code {response.status_code}: {response.text}")
            return {"numFound": 0, "docs": []}

        data = response.json()
        resp_data = data.get("response", {})
        return {
            "numFound": resp_data.get("numFound", 0),
            "docs": resp_data.get("docs", [])
        }
    except Exception as e:
        logger.error(f"Connection to Apache Solr failed: {e}")
        # Return empty list gracefully so frontend doesn't crash
        return {"numFound": 0, "docs": [], "error": "Search service temporarily unavailable"}

@app.post("/work-orders")
def create_work_order(wo: WorkOrderCreate):
    """Expose endpoint to generate new work orders from recommendations."""
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
    """Update status of work orders (e.g. mark completed)."""
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
