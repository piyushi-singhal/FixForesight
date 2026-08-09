# Docker Deployment

## Prerequisites

- Docker Engine 20+
- Docker Compose v2+

---

## ⚠️ Known Issue Before Starting

The `data/` directory is **not copied into the Docker image** by `backend/Dockerfile`. The prediction pipeline at startup (`run_predictions_pipeline()`) reads `data/engineered_ai4i.csv`. Without it, the pipeline will fail silently and no machine data will be pre-populated.

**Workaround:** Add a volume mount to docker-compose.yml:
```yaml
backend:
  volumes:
    - ./data:/app/data
```
Or add `COPY data/ /app/data/` to `backend/Dockerfile`.

---

## Start the Full Stack

```bash
docker-compose up --build
```

Verify all services are healthy:
```bash
docker-compose ps
```

Expected:
```
postgres    Up (healthy)   0.0.0.0:5432->5432/tcp
localstack  Up (healthy)   0.0.0.0:4566->4566/tcp
solr        Up (healthy)   0.0.0.0:8983->8983/tcp
backend     Up             0.0.0.0:8000->8000/tcp
frontend    Up             0.0.0.0:3000->80/tcp
```

---

## Access Points

| Service | URL |
|---|---|
| Frontend (React) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Documentation (Swagger) | http://localhost:8000/docs |
| Legacy Dashboard | http://localhost:8000 |
| Solr Admin | http://localhost:8983/solr |
| LocalStack | http://localhost:4566 |

---

## Stopping

```bash
# Stop only
docker-compose down

# Stop and remove volumes (full reset)
docker-compose down -v
```

---

## Rebuild a Single Service

```bash
docker-compose build backend
docker-compose up -d backend
```

---

## View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend
```
