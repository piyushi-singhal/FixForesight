# Roadmap

## P0 — Must Fix (Blockers)

| # | Task | Effort | Reference |
|---|---|---|---|
| P0-1 | Add `COPY data/ /app/data/` to backend Dockerfile | 5 min | KI-001 |
| P0-2 | Copy or mount `alembic.ini` into Docker image | 10 min | KI-002 |
| P0-3 | Verify full Docker stack with `data/` included | 30 min | KI-001 |

## P1 — Important (Complete the System)

| # | Task | Effort |
|---|---|---|
| P1-1 | Compute model monitoring metrics dynamically at inference time | 2 hours |
| P1-2 | Add `WorkOrderStatus` enum validation to Pydantic schema | 30 min |
| P1-3 | Fix postgres health check to actually test DB connectivity | 30 min |
| P1-4 | Write automated test for SQS → consumer → DB flow | 2 hours |
| P1-5 | Write automated test for Solr search correctness | 1 hour |
| P1-6 | Write automated test for SNS webhook → alerts table | 1 hour |
| P1-7 | Remove or archive `models/selected_features.pkl` | 5 min |
| P1-8 | Fix misleading comment in `backend/db/schema.sql` | 5 min |

## P2 — Engineering Quality

| # | Task | Effort |
|---|---|---|
| P2-1 | Split `frontend/src/App.jsx` into component files | 4 hours |
| P2-2 | Replace CORS `allow_origins=["*"]` with configurable list | 30 min |
| P2-3 | Replace `print()` logging with Python `logging` module | 2 hours |
| P2-4 | Add CI/CD pipeline (GitHub Actions) | 3 hours |
| P2-5 | Pin LocalStack image version (currently `latest`) | 5 min |
| P2-6 | Add Solr schema definition for type safety | 2 hours |
| P2-7 | Move all secrets/config to `.env` file | 1 hour |

## P3 — Enhancements

| # | Task | Effort |
|---|---|---|
| P3-1 | Add authentication layer (JWT tokens) | 1 day |
| P3-2 | Implement model drift detection | 2 days |
| P3-3 | Add model retraining pipeline trigger | 1 day |
| P3-4 | Implement incremental Solr indexing | 4 hours |
| P3-5 | Add parts inventory API and UI | 1 day |
| P3-6 | Add Prometheus metrics endpoint | 4 hours |
| P3-7 | Frontend UI tests with Playwright or Cypress | 2 days |
| P3-8 | Class imbalance handling (SMOTE or class_weight) to improve Recall | 4 hours |
| P3-9 | Lower prediction threshold (e.g., 0.3) to improve Recall for safety-critical use | 1 hour |

---

## Summary

The core system works end-to-end in local development. The two most impactful fixes before any Docker demonstration are **P0-1** (add `data/` to Docker image) and **P0-2** (fix alembic.ini path). Everything else is a quality improvement or feature enhancement.
