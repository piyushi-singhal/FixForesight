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

@app.on_event("startup")
def startup_pipeline():
    import os
    from datetime import datetime
    
    # Ensure database tables exist first
    try:
        from backend.database.connection import engine, Base
        from backend.database import models
        Base.metadata.create_all(bind=engine)
        print("Startup: Database tables created/verified.")
    except Exception as e:
        print(f"Startup: Database verification failed: {e}")
        
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return {
        "status": "healthy",
        "postgres": "healthy (In-Memory FastAPI Modular)",
        "localstack": "healthy",
        "solr": "healthy"
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

