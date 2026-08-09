# Known Issues

> Documented discrepancies between intended design, old documentation claims, and actual implementation.

---

## P0 — Must Fix Before Demo

### KI-001: `data/` not in Docker image

**Location:** `backend/Dockerfile`

**Issue:** The predictions pipeline reads `data/engineered_ai4i.csv` at startup. This file is not copied into the Docker image.

**Impact:** `POST /predictions/pipeline` and startup pipeline fail silently inside Docker. Dashboard shows no data.

**Fix:** Add to `backend/Dockerfile`:
```dockerfile
COPY data/ /app/data/
```
Or add a volume mount in `docker-compose.yml`.

---

### KI-002: Alembic.ini path may fail inside Docker

**Location:** `backend/main.py:startup_pipeline()`

**Issue:**
```python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
ini_path = os.path.join(project_root, "alembic.ini")
```
Inside Docker at WORKDIR `/app`, `__file__` = `/app/backend/main.py`, so `project_root` = `/app`, and `ini_path` = `/app/alembic.ini` — but `alembic.ini` is not in the Docker image.

**Fix:** Either COPY `alembic.ini` into Docker, or embed migration in startup.

---

### KI-003: Model monitoring metrics are hardcoded

**Location:** `backend/routes/analytics.py:get_model_monitoring()`

**Issue:**
```python
return {"accuracy": 0.9845, "precision": 0.885, "recall": 0.642, "f1": 0.7438, "roc_auc": 0.9618}
```

**Impact:** Values don't change with model updates. Presents false impression of live monitoring.

**Correction:** Values are accurate for the current `best_model.pkl` from `model_comparison.csv`. They are not fabricated — they just aren't dynamically computed.

---

## P1 — Important

### KI-004: Old README claims TensorFlow is the runtime model

**Location:** Various documentation files (not `docs/` — the new docs are correct)

**Issue:** Legacy docs claim TensorFlow/Keras inference. Actual runtime uses `GradientBoostingClassifier` (scikit-learn). TensorFlow is in `requirements.txt` but not installed in the actual `.venv`.

**Status:** Corrected in all new documentation.

---

### KI-005: `selected_features.pkl` is stale

**Location:** `models/selected_features.pkl`

**Issue:** This artifact exists from an older 4-feature training run. It is not used by the current inference code.

**Recommendation:** Delete or archive this file to avoid confusion.

---

### KI-006: schema.sql comment references TensorFlow

**Location:** `backend/db/schema.sql` line 23:
```sql
-- 2. Predictions Table (TensorFlow output target)
```

**Issue:** Misleading comment. The inference model is scikit-learn GradientBoosting, not TensorFlow.

**Fix:** Update comment to "ML model output (GradientBoostingClassifier)".

---

### KI-007: S3 bucket `iot-raw-data` created but unused

**Location:** `infra/localstack/init-resources.sh`

**Issue:** The S3 bucket is initialised but no code currently reads from or writes to it.

**Status:** ⚪ Infrastructure placeholder.

---

### KI-008: Postgres health check in GET /health always returns "healthy"

**Location:** `backend/main.py:get_health()`

**Issue:**
```python
return {"status": overall_status, "postgres": "healthy", ...}
```
Postgres status is hardcoded as "healthy" — no actual ping performed.

---

## P2 — Quality Improvements

### KI-009: `App.jsx` is 73 KB (monolithic)

**Location:** `frontend/src/App.jsx`

**Issue:** All React views and components in a single 73 KB file. Difficult to maintain.

**Recommendation:** Split into separate component files per view.

---

### KI-010: No input validation enum for WorkOrderStatusUpdate

**Location:** `backend/schemas/models.py`

**Issue:** `status: str` — any string accepted. Should be:
```python
from enum import Enum
class WorkOrderStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
```

---

### KI-011: CORS allow_origins = "*"

**Location:** `backend/main.py`

**Issue:** Wide-open CORS — acceptable for development, must be restricted for deployment.
