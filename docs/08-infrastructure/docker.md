# Docker

## Overview

FixForesight provides two Dockerfiles:

| File | Image Base | Serves |
|---|---|---|
| `backend/Dockerfile` | `python:3.10-slim` | FastAPI backend on port 8000 |
| `frontend/Dockerfile` | nginx | React SPA on port 80 |

---

## backend/Dockerfile

```dockerfile
FROM python:3.10-slim
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y curl build-essential libpq-dev

# Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY backend/  /app/backend/
COPY src/      /app/src/
COPY models/   /app/models/
COPY config.ini /app/

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build context:** `.` (project root)

**Files included:**
- `backend/` — FastAPI application
- `src/` — ML pipeline and sensor simulator
- `models/` — trained model artifacts (best_model.pkl, scaler.pkl)
- `config.ini` — configuration

**Files NOT included (known gap):**
- `data/` — CSV datasets — **prediction pipeline will fail at startup inside Docker**
- `alembic/` root configs — the `alembic.ini` is NOT in the image, but the code references `os.path.join(project_root, "alembic.ini")` which resolves from the container's filesystem

---

## frontend/Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

Serves compiled React SPA via nginx on port 80.

---

## Known Issues

1. **`data/` not in Docker image** — The backend Dockerfile does not `COPY data/`, so `run_predictions_pipeline()` cannot find `data/engineered_ai4i.csv` and will fail silently at startup.
2. **`alembic.ini` path** — `main.py` computes the alembic.ini path as `os.path.dirname(current_dir)/../alembic.ini`. Inside the container at WORKDIR=/app, this resolves to `/alembic.ini` which does not exist. Alembic migrations may fail inside Docker.
