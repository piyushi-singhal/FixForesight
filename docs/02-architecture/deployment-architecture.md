# Deployment Architecture

## Docker Compose Stack

Source: `docker-compose.yml` (verified directly).

### Services

#### postgres
| Property | Value |
|---|---|
| Image | `postgres:15-alpine` |
| Container | `postgres` |
| Port | `5432:5432` |
| Database | `pdm_db` |
| User | `postgres` |
| Init scripts | `backend/db/schema.sql`, `backend/db/seed.sql` |
| Volume | `postgres_data` (named volume) |
| Health check | `pg_isready -U postgres -d pdm_db` every 5s |
| Network | `pdm-network` |

> **Note:** The schema is initialised via `docker-entrypoint-initdb.d/` SQL scripts AND Alembic migrations run at backend startup. There is potential for drift between the SQL schema file and Alembic migration state.

#### localstack
| Property | Value |
|---|---|
| Image | `localstack/localstack:latest` |
| Container | `localstack` |
| Port | `4566:4566` |
| Services | `s3, sqs, sns` |
| Region | `us-east-1` |
| Init script | `infra/localstack/init-resources.sh` |
| Volume | `localstack_data` |
| Network | `pdm-network` |

Resources created on init:
- S3 bucket: `iot-raw-data`
- SQS queue: `sensor-events`
- SNS topic: `maintenance-alerts`
- SNS subscription: HTTP → `http://backend:8000/alerts/webhook`

#### solr
| Property | Value |
|---|---|
| Image | `solr:9-alpine` |
| Container | `solr` |
| Port | `8983:8983` |
| Core | `incidents` (created via `solr-precreate incidents`) |
| Volume | `solr_data` |
| Network | `pdm-network` |

#### backend
| Property | Value |
|---|---|
| Build context | `.` (project root) |
| Dockerfile | `backend/Dockerfile` |
| Container | `backend` |
| Port | `8000:8000` |
| Depends on | postgres (healthy), localstack (healthy), solr (healthy) |
| Network | `pdm-network` |

Environment variables:
```
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/pdm_db
AWS_ENDPOINT_URL=http://localstack:4566
AWS_ACCESS_KEY_ID=mock
AWS_SECRET_ACCESS_KEY=mock
AWS_DEFAULT_REGION=us-east-1
SOLR_URL=http://solr:8983/solr/incidents
```

Files copied into image (from `backend/Dockerfile`):
```
backend/   → /app/backend/
src/       → /app/src/
models/    → /app/models/
config.ini → /app/
```

> ⚠️ **Known Issue:** The `data/` directory is NOT copied into the Docker image. This means `run_predictions_pipeline()` will fail at startup inside Docker unless the CSV dataset is made available separately (e.g., via volume mount).

#### frontend
| Property | Value |
|---|---|
| Build context | `./frontend` |
| Dockerfile | `frontend/Dockerfile` |
| Container | `frontend` |
| Port | `3000:80` |
| Depends on | backend |
| Network | `pdm-network` |

---

## Volumes

| Volume | Used By | Purpose |
|---|---|---|
| `postgres_data` | postgres | Database persistence |
| `localstack_data` | localstack | SQS/SNS/S3 state persistence |
| `solr_data` | solr | Search index persistence |

---

## Network

Single bridge network: `pdm-network` (name: `pdm-network`).

All containers communicate by service name (DNS resolution within Docker).

---

## Known Issues

1. **`data/` not in Docker image** — `predictions_pipeline.py` reads `data/engineered_ai4i.csv` but this directory is not `COPY`'d in `backend/Dockerfile`.
2. **Mock AWS credentials in docker-compose** — `AWS_ACCESS_KEY_ID=mock` is in plain text. Acceptable for LocalStack (simulation) but should be moved to `.env` for production.
3. **LocalStack health check uses `awslocal`** — the health check may fail if `awslocal` is not present in the LocalStack container at the version pinned.

---

## Diagram

See [deployment-diagram.mmd](diagrams/deployment-diagram.mmd).
