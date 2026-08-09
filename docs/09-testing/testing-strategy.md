# Testing Strategy

## Overview

FixForesight has two test files at the project root:

| File | Classification | What It Tests |
|---|---|---|
| `tests_integration.py` | Component-level integration | Sensor simulator, feature engineering, ML model train/eval, recommendation engine, data pipeline — **in isolation from the database and API** |
| `tests_api_e2e.py` | API end-to-end | Full ML → PostgreSQL → FastAPI flow via HTTP calls to a running backend |

---

## Test Classification

### tests_integration.py — Component Tests

These tests exercise Python modules in the `src/` directory without a running server or database.

| Test | Function | Type |
|---|---|---|
| TEST 1 | `test_sensor_simulator()` | Component |
| TEST 2 | `test_feature_engineering(df)` | Component |
| TEST 3 | `test_ml_model(df_engineered)` | Component |
| TEST 4 | `test_recommendation_engine(df_engineered)` | Component |
| TEST 5 | `test_data_processing()` | Component |

> **Classification note:** Despite the file name `tests_integration.py`, these are component-level tests. They test individual modules but do not involve a database, HTTP server, or message broker. They do not prove the full system integrates correctly.

### tests_api_e2e.py — API End-to-End Tests

These tests require a running backend (`http://127.0.0.1:8000`) and a working database.

| Step | Endpoint | Validates |
|---|---|---|
| 1 | `POST /predictions/pipeline?limit=5` | Pipeline runs, returns success |
| 2 | `GET /predictions` | Predictions exist in DB |
| 3 | `GET /machines` | Machines exist in DB |
| 4 | `POST /work-orders` | Work order created |
| 5 | `PATCH /work-orders/{id}/status {in_progress}` | Status transition works |
| 6 | `PATCH /work-orders/{id}/status {completed}` | Completion works |

---

## What Is NOT Tested

| Gap | Impact |
|---|---|
| Solr search correctness | Cannot verify search returns accurate results |
| SQS → ML → DB flow | No automated test for the consumer thread path |
| SNS webhook | No test for SNS delivery to `/alerts/webhook` |
| Docker build correctness | No CI pipeline to verify clean Docker rebuild |
| Model loading in Docker | Not verified end-to-end |
| Frontend UI | No UI tests (no Cypress, Playwright, or similar) |
| Authentication | N/A — no auth implemented |
| Edge cases | No negative tests, boundary value tests |

---

## Running Tests

```bash
# Component tests (no server required)
cd /path/to/FixForesight
source .venv/bin/activate
python tests_integration.py

# API E2E tests (requires running backend)
# First start: ./.venv/bin/python -m uvicorn backend.main:app --port 8000
python tests_api_e2e.py
```

---

## Related Documents

- [Test Plan](test-plan.md)
- [Integration Testing](integration-testing.md)
- [Validation Checklist](validation-checklist.md)
