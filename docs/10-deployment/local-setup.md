# Local Setup

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| PostgreSQL | 15 | Database (or use Docker) |
| Git | any | Version control |

---

## Step 1 — Clone and Environment

```bash
git clone https://github.com/piyushi-singhal/FixForesight.git
cd FixForesight

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

---

## Step 2 — Database

### Option A: Use Docker for PostgreSQL only
```bash
docker run -d \
  --name postgres \
  -e POSTGRES_DB=pdm_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine
```

### Option B: Local PostgreSQL
```bash
psql -U postgres -c "CREATE DATABASE pdm_db;"
```

Apply schema:
```bash
psql -U postgres -d pdm_db -f backend/db/schema.sql
psql -U postgres -d pdm_db -f backend/db/seed.sql
```

---

## Step 3 — Run ML Pipeline (Optional — pre-populates DB)

```bash
# Feature engineering (if engineered_ai4i.csv doesn't exist)
cd src
python feature_engineering_pipeline.py
cd ..

# Training (if models not present)
cd models
python train_models.py
cd ..
```

---

## Step 4 — Start Backend

```bash
source .venv/bin/activate
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/pdm_db"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will:
1. Apply Alembic migrations
2. Run predictions pipeline (100 records)
3. Attempt Solr sync (fails gracefully if Solr not running)
4. Start SQS consumer thread (fails gracefully if LocalStack not running)

Dashboard available at: `http://localhost:8000`  
API docs at: `http://localhost:8000/docs`

---

## Step 5 — Start Frontend (Optional — React SPA)

```bash
cd frontend
npm install
npm start  # or npm run dev
```

React app available at: `http://localhost:3000`

---

## Step 6 — Run Tests

```bash
# Component tests
python tests_integration.py

# API E2E tests (backend must be running)
python tests_api_e2e.py
```
