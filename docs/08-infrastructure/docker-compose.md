# Docker Compose

## Overview

`docker-compose.yml` (project root) orchestrates the complete FixForesight stack.

---

## Service Dependency Order

```
postgres (healthy) ─┐
localstack (healthy)─┼──► backend ──► frontend
solr (healthy) ─────┘
```

---

## Starting the Stack

```bash
docker-compose up --build
```

Expected startup sequence:
1. `postgres` starts; health check passes when `pg_isready` succeeds
2. `localstack` starts; initialises S3 bucket, SQS queue, SNS topic via `init-resources.sh`
3. `solr` starts; creates `incidents` core
4. `backend` starts:
   - Applies Alembic migrations
   - Runs predictions pipeline (100 records from dataset)
   - Syncs data to Solr
   - SQS consumer thread begins polling
5. `frontend` starts; nginx serves compiled React app

---

## Network

All services on `pdm-network` (bridge). Services communicate by container name:
- `backend` connects to `postgres:5432`
- `backend` connects to `localstack:4566`
- `backend` connects to `solr:8983`
- `frontend` Webpack/nginx serves to host port `3000`

---

## Environment Variables (Backend)

| Variable | Value | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:postgres@postgres:5432/pdm_db` | Hardcoded credentials |
| `AWS_ENDPOINT_URL` | `http://localstack:4566` | LocalStack address |
| `AWS_ACCESS_KEY_ID` | `mock` | Mock credential |
| `AWS_SECRET_ACCESS_KEY` | `mock` | Mock credential |
| `AWS_DEFAULT_REGION` | `us-east-1` | |
| `SOLR_URL` | `http://solr:8983/solr/incidents` | Solr core URL |

---

## Volumes

| Volume | Container Path | Purpose |
|---|---|---|
| `postgres_data` | `/var/lib/postgresql/data` | Database persistence |
| `localstack_data` | `/var/lib/localstack` | LocalStack state |
| `solr_data` | `/var/solr/data` | Solr index persistence |

---

## Stopping & Cleanup

```bash
# Stop services
docker-compose down

# Stop and remove all volumes (full reset)
docker-compose down -v
```
