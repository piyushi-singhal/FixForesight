# Troubleshooting

## Common Issues

---

### Backend fails to start: "No module named backend"

**Cause:** Running uvicorn from wrong directory or without virtual env.

**Fix:**
```bash
cd /path/to/FixForesight
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

### "Pipeline failed: data/engineered_ai4i.csv not found"

**Cause:** Dataset file missing.

**Fix:**
```bash
cd src
python feature_engineering_pipeline.py
```
This generates `data/engineered_ai4i.csv` from the source dataset.

---

### Model loading warning: "ML model loading failed"

**Cause:** `models/best_model.pkl` or `models/scaler.pkl` not found.

**Fix:**
```bash
cd models
python train_models.py
```
Or verify the files exist:
```bash
ls -la models/best_model.pkl models/scaler.pkl
```

---

### PostgreSQL connection refused

**Cause:** PostgreSQL not running.

**Fix A (Docker):**
```bash
docker-compose up postgres
```

**Fix B (Local):**
```bash
brew services start postgresql  # macOS
```

**Note:** Backend automatically falls back to SQLite if PostgreSQL is unavailable.

---

### Alembic migration fails: "No such file or directory: alembic.ini"

**Cause:** Running from wrong directory; `alembic.ini` is in the project root.

**Fix:**
```bash
cd /path/to/FixForesight
alembic upgrade head
```

---

### Solr sync warning on startup

**Cause:** Solr not running (expected in local setup without Docker).

**Impact:** Search functionality unavailable. All other features work.

**Fix:**
```bash
docker-compose up solr
```

---

### SQS consumer thread fails to connect

**Cause:** LocalStack not running.

**Impact:** Real-time sensor simulation via SQS unavailable. Batch pipeline still works.

**Fix:**
```bash
docker-compose up localstack
```

---

### Frontend shows "Failed to fetch" errors

**Cause:** Backend not running on port 8000.

**Fix:** Start the backend:
```bash
uvicorn backend.main:app --port 8000
```

---

### Docker: No data in dashboard after `docker-compose up`

**Cause:** `data/` directory not in Docker image — predictions pipeline fails silently.

**Fix:** Add volume mount to docker-compose.yml:
```yaml
backend:
  volumes:
    - ./data:/app/data
```
Then `docker-compose up --build`.

---

### `GET /analytics/model-monitoring` returns hardcoded values

**Cause:** This is known — metrics are hardcoded in `backend/routes/analytics.py`.

**Note:** Values reflect the training evaluation results and are accurate for the current model.

---

### `tests_integration.py` fails with ImportError

**Cause:** `src/` not in Python path.

**Fix:** The test file adds it via:
```python
sys.path.insert(0, str(Path(__file__).parent / "src"))
```
Run from the project root directory.
