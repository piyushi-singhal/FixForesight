# Architecture Decision Records

> These records document actual technology choices made in the FixForesight repository. Rationale marked "inferred" cannot be directly evidenced in code comments but is reasonable given the context.

---

## ADR-001 — PostgreSQL as Primary Database

**Decision:** Use PostgreSQL 15 as the primary data store.

**Alternatives considered:** SQLite (simpler), MongoDB (schemaless)

**Rationale:**
- Relational model suits the structured entity relationships (machines → predictions → recommendations → work_orders)
- Foreign key constraints and cascade deletes enforce data integrity
- SQLAlchemy ORM provides portable abstractions
- SQLite fallback built into `connection.py` for local development without Docker

**Status:** Implemented ✅

---

## ADR-002 — FastAPI as Backend Framework

**Decision:** Use FastAPI for the REST API backend.

**Alternatives considered:** Flask, Django REST Framework

**Rationale:**
- Auto-generated OpenAPI docs (`/docs`, `/redoc`) — useful for development and demonstration
- Pydantic v2 validation for request/response schemas
- Async support for background tasks (SQS consumer, simulation)
- Type annotations align with Python 3.10+ ecosystem

**Status:** Implemented ✅

---

## ADR-003 — React + Redux Toolkit for Frontend

**Decision:** Use React with Redux Toolkit for state management.

**Alternatives considered:** Vue.js, plain JavaScript

**Rationale (inferred):**
- Redux Toolkit provides predictable state management for multiple data entities (machines, predictions, recommendations, alerts, work orders)
- TypeScript slices and services provide type safety
- Widely adopted in industry

**Status:** Implemented ✅ (with a parallel plain HTML/JS dashboard for local use)

---

## ADR-004 — LocalStack for AWS Service Simulation

**Decision:** Use LocalStack to simulate S3, SQS, and SNS locally.

**Alternatives considered:** Real AWS (cost), Mock libraries (limited fidelity)

**Rationale:**
- Demonstrates cloud-native architecture (SQS consumer, SNS pub/sub) without real AWS costs
- Production migration path: replace `AWS_ENDPOINT_URL` with real endpoint
- Enables SQS-based sensor event ingestion pattern

**Status:** Infrastructure implemented ✅; full end-to-end SQS flow 🟡 Partially tested

---

## ADR-005 — Apache Solr for Search

**Decision:** Use Apache Solr 9 for full-text search over incident data.

**Alternatives considered:** Elasticsearch, PostgreSQL full-text search

**Rationale (inferred):**
- Demonstrates enterprise search technology in the stack
- Production-grade full-text search with relevance ranking
- Docker-native deployment with `solr-precreate` for zero-config core creation

**Status:** Implemented ✅; schemaless mode (no custom schema defined)

---

## ADR-006 — GradientBoostingClassifier as Production Model

**Decision:** Use `sklearn.ensemble.GradientBoostingClassifier` as the production ML model (`models/best_model.pkl`).

**Evidence from code:** `models/model_comparison.csv` shows GradientBoosting wins on Accuracy (0.9845), Precision (0.8491), F1 (0.7438), and AUC (0.9618) vs RandomForest and LogisticRegression.

**Rationale:**
- Best overall metrics on the test set
- Fast inference (scikit-learn, no GPU required)
- Serializable to `.pkl` for portable deployment
- Feature importances available for explainability

**Status:** Implemented ✅

---

## ADR-007 — 5-Feature Canonical Inference Contract

**Decision:** Use exactly 5 raw sensor features for training and inference.

Features: `[air_temperature, process_temperature, rotational_speed, torque, tool_wear]`

**Rationale:**
- Direct sensor readings — no derived features needed for good performance
- Simplifies inference: no feature engineering computation at prediction time
- Eliminates training/inference skew

**Status:** Implemented ✅

---

## ADR-008 — Alembic for Database Migrations

**Decision:** Use Alembic (alongside SQLAlchemy) for database migrations.

**Rationale:**
- `Base.metadata.create_all()` doesn't handle schema evolution
- Alembic provides versioned migrations suitable for production-style deployments
- Applied at backend startup via `alembic upgrade head`

**Status:** Initialized ✅; migrations applied at startup

---

## ADR-009 — Docker Compose for Local Orchestration

**Decision:** Use Docker Compose to orchestrate the full stack.

**Rationale:**
- Single command (`docker-compose up`) to start all 5 services
- Named volumes for data persistence
- Health checks ensure service dependency order
- `pdm-network` bridge provides service DNS resolution

**Status:** Implemented ✅; known issue with `data/` not being in Docker image

---

## ADR-010 — RobustScaler for Feature Scaling

**Decision:** Use `sklearn.preprocessing.RobustScaler` instead of `StandardScaler`.

**Rationale:**
- Industrial sensor data may have outliers (equipment faults, sensor spikes)
- RobustScaler uses median and IQR — robust to outlier influence
- StandardScaler uses mean and std — sensitive to outliers

**Status:** Implemented ✅
