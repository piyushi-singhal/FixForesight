# Security Considerations

## Before Any Public Deployment

### Authentication
Add JWT or API key authentication:
```python
from fastapi.security import HTTPBearer
security = HTTPBearer()
```

Or use FastAPI's built-in OAuth2 support.

### CORS Restriction
```python
# Replace:
allow_origins=["*"]

# With:
allow_origins=["https://your-domain.com"]
```

### PostgreSQL Hardening
- Change default `postgres/postgres` credentials
- Create a least-privilege application user
- Enable SSL connections

### Network Isolation
- Do not expose PostgreSQL (5432) or LocalStack (4566) or Solr (8983) to the public internet
- Use an API gateway or reverse proxy in front of the FastAPI backend

### Input Validation
- Add field length constraints to Pydantic models
- Validate `status` field in `WorkOrderStatusUpdate` against allowed values enum
- Sanitize search query `q` before passing to Solr

### HTTPS
Configure nginx reverse proxy with SSL certificates (Let's Encrypt for free certs).
