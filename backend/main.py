from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.routes import (
    machines,
    predictions,
    recommendations,
    alerts,
    analytics,
    search,
    work_orders
)

app = FastAPI(title="FixForesight Predictive + Prescriptive Backend (Modular)")

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
