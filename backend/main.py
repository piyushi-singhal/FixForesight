# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.responses import HTMLResponse
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.routes import (
    machines,
    predictions,
    recommendations,
    alerts,
    analytics,
    search,
    work_orders,
    dashboard
)

app = FastAPI(title="FixForesight Predictive + Prescriptive Backend (Modular)")

def start_sqs_consumer():
    import threading
    import time
    import json
    import logging
    from backend.services.db_service import get_sqs_client, process_single_telemetry
    
    logger = logging.getLogger("sqs_consumer_thread")
    logger.setLevel(logging.INFO)
    
    def poll_sqs():
        logger.info("SQS Consumer Thread: starting...")
        sqs = None
        queue_url = None
        for attempt in range(12):
            try:
                sqs = get_sqs_client()
                queue_url = sqs.get_queue_url(QueueName="sensor-events")["QueueUrl"]
                logger.info(f"SQS Consumer Thread: connected to queue at {queue_url}")
                break
            except Exception as e:
                logger.warning(f"SQS Consumer Thread: queue check failed (attempt {attempt+1}/12): {e}")
                time.sleep(5.0)
                
        if not sqs or not queue_url:
            logger.error("SQS Consumer Thread: failed to resolve queue sensor-events. Exiting thread.")
            return
            
        while True:
            try:
                response = sqs.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=5,
                    WaitTimeSeconds=5
                )
                messages = response.get("Messages", [])
                for msg in messages:
                    body_str = msg.get("Body", "")
                    try:
                        data = json.loads(body_str)
                        machine_id = data.get("machine_id", "M101")
                        air_temp = float(data.get("air_temperature"))
                        proc_temp = float(data.get("process_temperature"))
                        speed = int(data.get("rotational_speed"))
                        torque = float(data.get("torque"))
                        wear = float(data.get("tool_wear"))
                        
                        logger.info(f"SQS Consumer: processing telemetry event for {machine_id}")
                        process_single_telemetry(machine_id, air_temp, proc_temp, speed, torque, wear)
                    except Exception as parse_err:
                        logger.warning(f"SQS Consumer: failed to process telemetry body: {parse_err}")
                        
                    # Delete message from SQS
                    try:
                        sqs.delete_message(
                            QueueUrl=queue_url,
                            ReceiptHandle=msg["ReceiptHandle"]
                        )
                    except Exception as del_err:
                        logger.warning(f"SQS Consumer: failed to delete message: {del_err}")
            except Exception as loop_err:
                logger.warning(f"SQS Consumer Thread loop error: {loop_err}")
                time.sleep(2.0)

    t = threading.Thread(target=poll_sqs, daemon=True)
    t.start()

@app.on_event("startup")
def startup_pipeline():
    import os
    from datetime import datetime
    
    # Start the SQS consumer thread
    try:
        start_sqs_consumer()
        print("Startup: SQS Consumer background thread started.")
    except Exception as sqs_thread_err:
        print(f"Startup: SQS Consumer background thread initialization failed: {sqs_thread_err}")
        
    # Ensure database migrations are applied first
    try:
        from alembic.config import Config
        from alembic import command
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        ini_path = os.path.join(project_root, "alembic.ini")
        
        print(f"Startup: Applying database migrations using Alembic config: {ini_path}")
        alembic_cfg = Config(ini_path)
        command.upgrade(alembic_cfg, "head")
        print("Startup: Database migrations applied successfully.")
    except Exception as e:
        print(f"Startup: Database migrations failed: {e}")
        
    lock_file = os.path.join(os.path.dirname(__file__), "..", "tmp", "pipeline.lock")
    run_pipeline = not os.path.exists(lock_file)
    
    if run_pipeline:
        os.makedirs(os.path.dirname(lock_file), exist_ok=True)
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))
            
        print("Startup: Running predictions/recommendations pipeline...")
        result_file = os.path.join(os.path.dirname(__file__), "..", "tmp", "pipeline_result.json")
        
        try:
            from backend.services import db_service
            from backend.database.connection import SessionLocal
            from backend.database.models import Prediction, Recommendation
            
            # Run pipeline
            count = db_service.run_predictions_pipeline(limit=100)
            
            # Fetch samples to verify
            sess = SessionLocal()
            try:
                preds = sess.query(Prediction).limit(5).all()
                recs = sess.query(Recommendation).limit(5).all()
                
                preds_sample = [
                    {
                        "machine_id": p.machine_id,
                        "failure_probability": p.failure_probability,
                        "predicted_failure": p.predicted_failure,
                        "time_to_failure": p.time_to_failure
                    } for p in preds
                ]
                recs_sample = [
                    {
                        "machine_id": r.machine_id,
                        "recommendation": r.recommendation,
                        "priority": r.priority,
                        "confidence": r.confidence
                    } for r in recs
                ]
            finally:
                sess.close()
                
            import json
            with open(result_file, "w") as f:
                json.dump({
                    "status": "success",
                    "processed_records": count,
                    "predictions_sample": preds_sample,
                    "recommendations_sample": recs_sample,
                    "timestamp": str(datetime.utcnow())
                }, f, indent=2)
                
            print(f"Startup: Pipeline completed successfully. Written results to {result_file}")
        except Exception as e:
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                except:
                    pass
            import json
            with open(result_file, "w") as f:
                json.dump({
                    "status": "error",
                    "error": str(e),
                    "timestamp": str(datetime.utcnow())
                }, f, indent=2)
            print(f"Startup: Pipeline failed: {e}")
            
    # Trigger Solr Synchronization on EVERY startup
    try:
        from backend.services import db_service
        db_service.sync_data_to_solr()
        print("Startup: Database records successfully synced to Apache Solr.")
    except Exception as solr_err:
        print(f"Startup: Solr sync warning: {solr_err}")


# Enable CORS for cross-origin frontend requests
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]
env_origins = os.environ.get("ALLOWED_ORIGINS")
if env_origins:
    allowed_origins = [o.strip() for o in env_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves UI Dashboard
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

# Health check
@app.get("/health")
def get_health():
    import requests
    import os
    
    # Check Solr
    solr_status = "healthy"
    solr_url = os.environ.get("SOLR_URL", "http://localhost:8983/solr/incidents")
    solr_base = solr_url.split("/incidents")[0] if "/incidents" in solr_url else solr_url
    try:
        r = requests.get(f"{solr_base}/admin/cores?action=STATUS", timeout=1.0)
        if r.status_code != 200:
            solr_status = "unhealthy"
    except Exception:
        solr_status = "unhealthy"

    # Check LocalStack
    localstack_status = "healthy"
    try:
        from backend.services.db_service import get_sqs_client
        sqs = get_sqs_client()
        sqs.list_queues(MaxResults=1)
    except Exception:
        localstack_status = "unhealthy"

    # Check PostgreSQL
    postgres_status = "healthy"
    try:
        from backend.database.connection import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except Exception:
        postgres_status = "unhealthy"

    overall_status = "healthy"
    if solr_status == "unhealthy" or localstack_status == "unhealthy" or postgres_status == "unhealthy":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "postgres": postgres_status,
        "localstack": localstack_status,
        "solr": solr_status
    }

# Register Contract routers
app.include_router(machines.router)
app.include_router(predictions.router)
app.include_router(recommendations.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(search.router)
app.include_router(work_orders.router)
app.include_router(dashboard.router)

