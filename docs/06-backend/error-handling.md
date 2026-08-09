# Error Handling

## HTTP Error Responses

| Endpoint | Code | Trigger |
|---|---|---|
| `GET /machines/{machine_id}/risk` | 404 | Machine not found in DB |
| `PATCH /work-orders/{id}/status` | 404 | Work order not found (`ValueError` from service) |

All other errors return FastAPI default 422 (validation error) or 500 (internal server error).

---

## Model Loading Failure

If `best_model.pkl` or `scaler.pkl` cannot be loaded at startup, `db_service.py` sets `MODEL_AVAILABLE = False` and falls back to rule-based prediction:

```python
# Rule-based fallback logic in predict_machine_failure()
if wear > 200 or torque > 70 or speed < 1200 or temp_diff > 15:
    prob = 0.85  # high probability
else:
    prob = 0.1   # low probability
```

---

## Database Connection Failure

`backend/database/connection.py` falls back to SQLite if PostgreSQL is unavailable:
```python
# Falls back to:
DATABASE_URL = f"sqlite:///{db_file}"
# db_file = project_root/pdm_db.db
```

---

## SQS Consumer Error Handling

The SQS consumer thread catches all exceptions per iteration:
```python
except Exception as loop_err:
    logger.warning(f"SQS Consumer Thread loop error: {loop_err}")
    time.sleep(2.0)  # Backoff before retry
```

---

## Known Error Handling Gaps

1. **No authentication** — any client can call any endpoint.
2. **CORS `allow_origins=["*"]`** — all origins allowed; a security risk if deployed publicly.
3. **Postgres health check** — `GET /health` always returns `"postgres": "healthy"` even if DB is actually unreachable.
4. **Pipeline exception during startup** — if the prediction pipeline fails, the lock file is removed and the error is logged but the application continues to run.
