# System Architecture

## Overview

FixForesight uses a layered architecture with clear separation between:

1. **Data Plane** — CSV datasets, sensor simulation, SQS messages
2. **ML Plane** — feature engineering, model inference, recommendation engine
3. **Application Plane** — FastAPI backend, PostgreSQL, Solr
4. **Presentation Plane** — React + Redux frontend dashboard

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                │
│  CSV Dataset (data/)          Sensor Simulator (src/sensor_         │
│  AI4I 2020 (10,000 rows)      simulator.py)                         │
└───────────────┬───────────────────────────┬─────────────────────────┘
                │ batch                     │ SQS events
                ▼                           ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        ML PLANE                                       │
│                                                                       │
│  feature_engineering_pipeline.py ──► ml_pipeline.py                  │
│  (temp_diff, power, wear_rate…)     (GradientBoosting, trained on    │
│                                      5 canonical features)           │
│                      │                                               │
│                      ▼                                               │
│           models/best_model.pkl + models/scaler.pkl                  │
│                      │                                               │
│                      ▼                                               │
│           recommendation_engine.py (rule-based)                      │
└──────────────────────┬────────────────────────────────────────────────┘
                       │ predictions + recommendations
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      APPLICATION PLANE                               │
│                                                                      │
│  FastAPI (backend/main.py)                                           │
│    ├── /machines          ├── /predictions       ├── /recommendations│
│    ├── /alerts            ├── /work-orders        ├── /analytics     │
│    ├── /dashboard         ├── /search             └── /health        │
│    └── SQS consumer thread (daemon)                                  │
│                                                                      │
│  PostgreSQL (pdm_db)          Apache Solr (incidents core)           │
│  ├── machines                 └── incidents search index             │
│  ├── predictions                                                     │
│  ├── recommendations                                                 │
│  ├── alerts                                                          │
│  ├── work_orders                                                     │
│  └── parts_inventory                                                 │
└──────────────────────┬───────────────────────────────────────────────┘
                       │ HTTP REST + JSON
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    PRESENTATION PLANE                                │
│                                                                      │
│  React + Redux Toolkit (frontend/src/)                               │
│  ├── Dashboard (fleet summary)                                       │
│  ├── Machine Detail (telemetry + risk + predictions)                 │
│  ├── Recommendations                                                 │
│  ├── Alerts                                                          │
│  ├── Work Orders                                                     │
│  ├── Analytics (feature importance + model metrics)                  │
│  └── Search (Solr-backed)                                            │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Infrastructure Layer (Docker Compose)

| Container | Image | Port | Role |
|---|---|---|---|
| `postgres` | postgres:15-alpine | 5432 | Primary data store |
| `localstack` | localstack/localstack:latest | 4566 | S3, SQS, SNS simulation |
| `solr` | solr:9-alpine | 8983 | Full-text search index |
| `backend` | python:3.10-slim (custom) | 8000 | FastAPI application |
| `frontend` | nginx (built from Dockerfile) | 3000 | Static React app |

All containers share the `pdm-network` bridge network.

---

## Key Design Decisions

- **Stateful startup pipeline** — on backend start, Alembic migrations are applied, then the prediction pipeline runs (locked via `tmp/pipeline.lock`), then Solr is synced.
- **SQLite fallback** — if PostgreSQL is unavailable, `connection.py` automatically falls back to a local SQLite file (`pdm_db.db`).
- **SQS consumer daemon thread** — a background thread continuously long-polls the `sensor-events` SQS queue and processes individual telemetry events through the ML pipeline.
- **SNS → FastAPI webhook** — LocalStack subscribes the backend `/alerts/webhook` endpoint to the `maintenance-alerts` SNS topic.

---

## Diagrams

- [System Architecture Diagram (Mermaid)](diagrams/system-architecture.mmd)
- [End-to-End Data Flow](end-to-end-data-flow.md)
- [Deployment Architecture](deployment-architecture.md)
- [Sequence Flows](sequence-flows.md)
