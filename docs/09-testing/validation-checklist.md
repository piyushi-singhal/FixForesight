# Validation Checklist

> This checklist must be verified manually or via `tests_api_e2e.py` before any release.

---

## ML Pipeline

- [ ] ML model loads from `models/best_model.pkl` without error
- [ ] Scaler loads from `models/scaler.pkl` without error
- [ ] `predict_machine_failure(298, 310, 1500, 40, 100)` returns a valid probability (0–1)
- [ ] Failure type is correctly classified for tool_wear > 180
- [ ] Failure type is correctly classified for heat dissipation (process_temp - air_temp > 15K)
- [ ] Time-to-failure bucket returns "6 Hours" when probability > 0.9
- [ ] Recommendation generated matches failure probability threshold rules

## Database

- [ ] `alembic upgrade head` runs without error
- [ ] All 6 tables exist: `machines`, `predictions`, `recommendations`, `alerts`, `work_orders`, `parts_inventory`
- [ ] Machine INSERT succeeds
- [ ] Prediction INSERT (linked to machine) succeeds
- [ ] Recommendation INSERT (linked to machine + prediction) succeeds
- [ ] Work order INSERT succeeds
- [ ] Work order status update (open → in_progress) succeeds
- [ ] Work order status update (in_progress → completed) succeeds with `completed_at` populated

## FastAPI Endpoints

- [ ] `GET /health` returns 200
- [ ] `GET /machines` returns list of machines
- [ ] `GET /predictions` returns list of predictions
- [ ] `GET /recommendations` returns list of recommendations
- [ ] `GET /alerts` returns list (may be empty)
- [ ] `GET /work-orders` returns list
- [ ] `POST /work-orders` creates a work order, returns work_order_id
- [ ] `PATCH /work-orders/{id}/status` updates status successfully
- [ ] `GET /analytics` returns fleet status counts
- [ ] `GET /analytics/feature-importance` returns feature importance dict
- [ ] `GET /analytics/model-monitoring` returns accuracy/precision/recall/f1/roc_auc
- [ ] `GET /dashboard` returns fleet summary
- [ ] `GET /search?q=*:*` returns search results (or empty if Solr down)
- [ ] `POST /predictions/pipeline?limit=5` runs pipeline and stores records

## Frontend

- [ ] Dashboard page loads without console errors
- [ ] Machine fleet cards are populated from API
- [ ] Machine detail view shows telemetry, risk, predictions, recommendations
- [ ] Feature importance bars render correctly
- [ ] Model monitoring metrics display correctly
- [ ] Work order form submission creates a work order
- [ ] In-progress and completed status buttons work
- [ ] Search input returns results

## Infrastructure (Docker)

- [ ] `docker-compose up --build` completes without errors
- [ ] PostgreSQL health check passes
- [ ] LocalStack health check passes
- [ ] Solr health check passes
- [ ] Backend startup log shows "Database migrations applied successfully"
- [ ] Backend startup log shows "Pipeline completed successfully"
- [ ] Backend startup log shows "Database records successfully synced to Apache Solr"
- [ ] SQS consumer thread starts successfully
- [ ] `POST /machines/M101/simulate?count=3` sends events that appear in machine telemetry

## End-to-End Pipeline

- [ ] Run `python tests_api_e2e.py` — all 6 assertions pass
- [ ] Run `python tests_integration.py` — all 5 component tests pass
- [ ] Full pipeline: dataset → ML → PostgreSQL → API → frontend displays data
- [ ] SQS flow: simulate → SQS event → consumer → predict → DB updated

## Security & Configuration

- [ ] `.env` file is not committed to git (check `.gitignore`)
- [ ] No hardcoded production passwords in source code
- [ ] `SECRET_KEY`, database passwords, AWS keys not exposed in documentation
