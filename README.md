# FixForesight

> **Predictive and Prescriptive Maintenance System for Industrial Machinery**

FixForesight ingests industrial sensor telemetry, predicts equipment failures using machine learning, prescribes targeted maintenance actions, and delivers results through a REST API and browser dashboard. It is built to demonstrate an end-to-end ML system with a cloud-native simulated infrastructure stack.

---

## Architecture

```
Sensor Telemetry / CSV Dataset
         ↓
Feature Engineering  (src/feature_engineering_pipeline.py)
         ↓
GradientBoostingClassifier  (models/best_model.pkl + scaler.pkl)
         ↓
Failure Probability + Failure Type + Time-to-Failure
         ↓
Recommendation Engine  (src/recommendation_engine.py)
         ↓
PostgreSQL ←—→ FastAPI (:8000)
         ↓
React + Redux Dashboard (:3000)
```

```
LocalStack (SQS/SNS/S3) ←—→ Sensor Simulator
                                    ↓
                            SQS Consumer Thread
                                    ↓
                            ML Inference → PostgreSQL
                                    ↓
                            SNS Alert → /alerts/webhook
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML Framework | scikit-learn (GradientBoostingClassifier, RobustScaler) |
| Backend API | FastAPI + Uvicorn |
| Database | PostgreSQL 15 + SQLAlchemy ORM + Alembic |
| Cloud Simulation | LocalStack (S3, SQS, SNS) |
| Search | Apache Solr 9 |
| Frontend | React + Redux Toolkit + TypeScript |
| Containerisation | Docker + Docker Compose |
| Dataset | AI4I 2020 Predictive Maintenance (UCI ML Repository) |

---

## Repository Structure

```
FixForesight/
├── src/                    ← ML pipeline, sensor simulator, feature engineering
├── models/                 ← Trained model artifacts (best_model.pkl, scaler.pkl)
├── backend/                ← FastAPI application
│   ├── routes/             ← API endpoints
│   ├── services/           ← Business logic + ML inference
│   ├── database/           ← SQLAlchemy models + connection
│   └── schemas/            ← Pydantic request/response models
├── frontend/               ← React SPA + HTML dashboard
├── data/                   ← Dataset CSV files
├── infra/                  ← LocalStack init scripts
├── docs/                   ← Full documentation
├── docker-compose.yml
├── alembic.ini
└── requirements.txt
```

---

## Quick Start

### Local Development (no Docker required)

```bash
git clone https://github.com/piyushi-singhal/FixForesight.git
cd FixForesight

# Setup environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Start backend (uses SQLite fallback if no Postgres)
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Open dashboard: http://localhost:8000
```

### Docker (Full Stack)

> ⚠️ **See [known issue](docs/14-project-status/known-issues.md#ki-001):** Add `COPY data/ /app/data/` to `backend/Dockerfile` before running.

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Dashboard | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| React App | http://localhost:3000 |
| Solr Admin | http://localhost:8983/solr |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/machines` | All machines with telemetry + predictions |
| GET | `/machines/{id}/risk` | Risk assessment for a machine |
| POST | `/machines/{id}/simulate` | Trigger SQS sensor simulation |
| GET | `/predictions` | All failure predictions |
| POST | `/predictions/pipeline` | Run batch prediction pipeline |
| GET | `/recommendations` | All maintenance recommendations |
| GET | `/alerts` | All system alerts |
| POST | `/alerts/webhook` | SNS alert webhook receiver |
| GET | `/work-orders` | All work orders |
| POST | `/work-orders` | Create work order |
| PATCH | `/work-orders/{id}/status` | Update work order status |
| GET | `/analytics` | Fleet status summary |
| GET | `/analytics/feature-importance` | ML feature importances |
| GET | `/analytics/model-monitoring` | Model evaluation metrics |
| GET | `/dashboard` | Dashboard KPIs |
| GET | `/search?q=` | Full-text search (Solr) |
| GET | `/health` | System health check |

---

## ML Pipeline

- **Dataset:** AI4I 2020 Predictive Maintenance — 10,000 rows, ~3.4% failure rate
- **Feature contract:** 5 raw features: `air_temperature, process_temperature, rotational_speed, torque, tool_wear`
- **Scaler:** `RobustScaler` (robust to sensor outliers)
- **Models trained:** GradientBoosting, RandomForest, LogisticRegression
- **Production model:** GradientBoostingClassifier (`models/best_model.pkl`)

| Metric | Value |
|---|---|
| Accuracy | 98.45% |
| Precision | 84.91% |
| Recall | 66.18% |
| F1 | 74.38% |
| ROC-AUC | 0.9618 |

---

## Database

**PostgreSQL `pdm_db`** — 6 tables:

`machines` → `predictions` → `recommendations` → `work_orders`  
`machines` → `alerts`  
`parts_inventory` (standalone)

Schema managed by Alembic migrations (`alembic upgrade head` at startup).

---

## Testing

```bash
# Component tests (no server required)
python tests_integration.py

# API end-to-end tests (requires running backend)
python tests_api_e2e.py
```

---

## Documentation

Full engineering-grade documentation: **[docs/README.md](docs/README.md)**

| Section | Link |
|---|---|
| Project Overview | [docs/01-project-overview/](docs/01-project-overview/project-overview.md) |
| System Architecture | [docs/02-architecture/](docs/02-architecture/system-architecture.md) |
| Database Design + ER Diagram | [docs/03-database/](docs/03-database/database-design.md) |
| Data Engineering | [docs/04-data-engineering/](docs/04-data-engineering/data-pipeline.md) |
| Machine Learning | [docs/05-machine-learning/](docs/05-machine-learning/ml-overview.md) |
| Backend API Reference | [docs/06-backend/](docs/06-backend/api-reference.md) |
| Frontend Architecture | [docs/07-frontend/](docs/07-frontend/frontend-architecture.md) |
| Infrastructure (Docker/SQS/Solr) | [docs/08-infrastructure/](docs/08-infrastructure/docker.md) |
| Testing | [docs/09-testing/](docs/09-testing/testing-strategy.md) |
| Deployment | [docs/10-deployment/](docs/10-deployment/local-setup.md) |
| Security | [docs/11-security/](docs/11-security/security-overview.md) |
| Architecture Decisions | [docs/12-architecture-decisions/](docs/12-architecture-decisions/architecture-decision-records.md) |
| Troubleshooting | [docs/13-troubleshooting/](docs/13-troubleshooting/troubleshooting.md) |
| Project Status & Roadmap | [docs/14-project-status/](docs/14-project-status/current-status.md) |

---

## Current Status

| Component | Status |
|---|---|
| ML pipeline (training + inference) | ✅ Complete |
| FastAPI backend (all endpoints) | ✅ Complete |
| Database (PostgreSQL + Alembic) | ✅ Complete |
| React + HTML dashboards | ✅ Complete |
| Work order lifecycle | ✅ Complete |
| SQS consumer thread | ✅ Complete |
| SNS webhook | ✅ Complete |
| Solr search | ✅ Complete |
| Docker stack | 🟡 Partial (`data/` not in image) |
| Model monitoring (live) | 🟡 Partial (hardcoded metrics) |
| Authentication | ❌ Not implemented |

See [Known Issues](docs/14-project-status/known-issues.md) and [Roadmap](docs/14-project-status/roadmap.md).

---

## Known Limitations

1. **No authentication** — all API endpoints are open
2. **`data/` not in Docker image** — startup pipeline fails in full Docker deployment
3. **Model monitoring metrics are hardcoded** — not computed dynamically
4. **S3 bucket exists but is unused** — placeholder only
5. **Batch pipeline, not streaming** — primary data path reads CSV; SQS handles individual events

---

*Built with scikit-learn, FastAPI, PostgreSQL, React, LocalStack, Apache Solr, and Docker.*
