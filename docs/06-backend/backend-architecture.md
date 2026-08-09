# Backend Architecture

## Overview

The backend is a **FastAPI** application (`backend/main.py`) serving as the API layer between the ML pipeline and the frontend dashboard.

---

## Entry Point

`backend/main.py` — application factory.

### Responsibilities
1. **App creation** — `FastAPI(title="FixForesight Predictive + Prescriptive Backend (Modular)")`
2. **Startup hook** — `@app.on_event("startup") startup_pipeline()` orchestrates SQS consumer, Alembic migrations, prediction pipeline, and Solr sync
3. **CORS** — `CORSMiddleware` with `allow_origins=["*"]` (wide open — see Security)
4. **Static serve** — serves `frontend/public/index.html` at `GET /` and `GET /index.html`
5. **Router registration** — includes all 8 route modules

---

## Layer Architecture

```
HTTP Request
     ↓
FastAPI Route Handler (backend/routes/*.py)
     ↓
Service Layer (backend/services/db_service.py)
     ↓
SQLAlchemy ORM (backend/database/models.py)
     ↓
PostgreSQL (or SQLite fallback)
```

---

## Directory Structure

```
backend/
├── main.py                 ← App factory + startup
├── routes/
│   ├── machines.py         ← /machines
│   ├── predictions.py      ← /predictions
│   ├── recommendations.py  ← /recommendations
│   ├── alerts.py           ← /alerts
│   ├── analytics.py        ← /analytics
│   ├── work_orders.py      ← /work-orders
│   ├── search.py           ← /search
│   └── dashboard.py        ← /dashboard
├── services/
│   └── db_service.py       ← All DB queries + ML inference + AWS clients
├── database/
│   ├── connection.py       ← SQLAlchemy engine (Postgres + SQLite fallback)
│   ├── models.py           ← ORM table definitions
│   └── queries.py          ← Query helper functions
├── schemas/
│   └── models.py           ← Pydantic request/response schemas
├── db/
│   ├── schema.sql          ← Docker init SQL
│   └── seed.sql            ← Seed data SQL
└── alembic/                ← Migration files
```

---

## Service Layer (db_service.py)

`db_service.py` (1,118 lines) is the central service module. It handles:
- ML model loading at import time
- All database read/write functions
- SQS/SNS client creation
- Solr synchronization
- `predict_machine_failure()` inference function

---

## Health Check

`GET /health` returns:
```json
{
  "status": "healthy|degraded",
  "postgres": "healthy",
  "localstack": "healthy|unhealthy",
  "solr": "healthy|unhealthy"
}
```

- `postgres` is always `"healthy"` (no actual ping in current implementation)
- `localstack` checked via `sqs.list_queues()`
- `solr` checked via HTTP GET to `/solr/admin/cores`

---

## Related Documents

- [API Reference](api-reference.md)
- [API Contracts](api-contracts.md)
- [Error Handling](error-handling.md)
