# Environment Configuration

## Environment Variables

### Backend

| Variable | Default (local) | Docker Value | Description |
|---|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/pdm_db` | `postgresql://postgres:postgres@postgres:5432/pdm_db` | PostgreSQL connection string |
| `AWS_ENDPOINT_URL` | `http://localhost:4566` | `http://localstack:4566` | LocalStack endpoint |
| `AWS_ACCESS_KEY_ID` | `mock` | `mock` | Mock AWS key (LocalStack only) |
| `AWS_SECRET_ACCESS_KEY` | `mock` | `mock` | Mock AWS secret (LocalStack only) |
| `AWS_DEFAULT_REGION` | `us-east-1` | `us-east-1` | AWS region |
| `SOLR_URL` | `http://localhost:8983/solr/incidents` | `http://solr:8983/solr/incidents` | Solr core URL |

### Local .env File

The project has a `.env` file (listed in `.gitignore`). Load it with:
```bash
export $(cat .env | xargs)
```

---

## Configuration Files

| File | Purpose |
|---|---|
| `.env` | Local environment variables (NOT committed) |
| `config.ini` | Application configuration (see structure below) |
| `alembic.ini` | Alembic migration configuration |
| `backend/requirements.txt` | Backend Python dependencies |
| `requirements.txt` | Root-level Python dependencies (ML + dev tools) |

---

## Production Considerations

For any real deployment:
1. Replace mock AWS credentials with real IAM credentials
2. Use a secrets manager (AWS Secrets Manager, HashiCorp Vault)
3. Restrict CORS `allow_origins` to specific domains
4. Set `DATABASE_URL` to a managed PostgreSQL instance
5. Enable SSL for all endpoints
6. Add authentication (OAuth2, API keys)
