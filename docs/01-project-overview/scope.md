# Scope

## In Scope

### Data Layer
- AI4I 2020 dataset ingestion and cleaning (`data/`)
- Feature engineering pipeline (`src/feature_engineering_pipeline.py`, `src/engineer_features.py`)
- Sensor data simulator (`src/sensor_simulator.py`) — generates realistic telemetry with five failure modes

### Machine Learning
- GradientBoostingClassifier training and serialization (`models/train_models.py`, `src/ml_pipeline.py`)
- RandomForest as comparison model
- 5-feature inference contract: air_temperature, process_temperature, rotational_speed, torque, tool_wear
- Failure probability + failure type + time-to-failure estimation

### Backend API
All endpoints defined in `backend/routes/` and registered in `backend/main.py`:
- Machines, Predictions, Recommendations, Alerts, Work Orders, Analytics, Dashboard, Search

### Frontend Dashboard
- React application (`frontend/src/App.jsx`) with Redux Toolkit state management
- Fleet overview, machine detail, predictions, recommendations, alerts, work orders, search, analytics

### Infrastructure (Simulated)
- PostgreSQL database (via Docker or local)
- LocalStack: S3 bucket (`iot-raw-data`), SQS queue (`sensor-events`), SNS topic (`maintenance-alerts`)
- Apache Solr (`incidents` core) for full-text search

### Testing
- Component-level integration tests (`tests_integration.py`)
- API end-to-end tests (`tests_api_e2e.py`)

---

## Out of Scope

| Area | Reason |
|---|---|
| Real AWS cloud deployment | LocalStack only; no real AWS credentials used |
| Physical sensor hardware | No IoT SDK, OPC-UA, or MQTT integration |
| Production-grade autoscaling | Single-node Docker Compose only |
| Authentication / Authorization | No auth layer implemented (known gap) |
| Real-time streaming at scale | Batch file-based pipeline; SQS consumer thread handles individual events |
| Multi-machine Alembic migrations in CI | Migration applied at startup via `alembic upgrade head` |
| Mobile application | Web dashboard only |

---

## Related Documents

- [Objectives](objectives.md)
- [Requirements](requirements.md)
- [Known Issues](../14-project-status/known-issues.md)
