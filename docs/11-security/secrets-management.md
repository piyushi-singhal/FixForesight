# Secrets Management

## Current State

| Secret | Where Stored | Committed? |
|---|---|---|
| PostgreSQL password (`postgres`) | `docker-compose.yml` | ✅ Yes (mock value) |
| AWS Access Key ID (`mock`) | `docker-compose.yml` | ✅ Yes (mock value) |
| AWS Secret Access Key (`mock`) | `docker-compose.yml` | ✅ Yes (mock value) |
| Database URL | `backend/database/connection.py` default | ✅ Yes (default only) |
| Real credentials | `.env` file | ❌ No (.gitignored) |

## Recommendation

For any environment beyond local development:
1. Remove hardcoded values from `docker-compose.yml`
2. Use Docker secrets or an `.env` file:
   ```yaml
   # docker-compose.yml
   backend:
     env_file: .env
   ```
3. Never commit `.env` — ensure `.gitignore` includes it (it currently does)

## Current .gitignore

The `.gitignore` includes `.env`, `*.pkl`, `*.db`, and Python cache directories.
