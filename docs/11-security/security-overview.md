# Security Overview

> **Disclaimer:** FixForesight is a prototype/demonstration system. It has **no authentication layer** and should not be deployed publicly without addressing the issues documented here.

---

## Known Security Gaps

### Critical

| Issue | Location | Risk |
|---|---|---|
| No authentication | All API endpoints | Any client can read/write all data |
| `CORS allow_origins=["*"]` | `backend/main.py` | Cross-origin requests from any domain |
| Mock AWS credentials in docker-compose | `docker-compose.yml` | Exposure of config file reveals `AWS_ACCESS_KEY_ID=mock` (LocalStack only, but pattern is bad) |

### High

| Issue | Location | Risk |
|---|---|---|
| Hardcoded DB credentials | `docker-compose.yml`, `connection.py` default | `postgres/postgres` default — must be changed for any real deployment |
| SQLite fallback with sensitive data | `connection.py` | Falls back to a local SQLite file at project root which may not be protected |
| No input validation on work order fields | `schemas/models.py WorkOrderRequest` | All fields Optional with no length limits |

### Medium

| Issue | Location | Risk |
|---|---|---|
| Solr admin UI exposed | Port 8983 | No auth on Solr admin interface |
| LocalStack exposed | Port 4566 | No auth on AWS service simulation |
| No rate limiting | FastAPI middleware | Potential for API abuse |

---

## What Is Safe (for Local/Demo Use)

- All AWS credentials are mock values for LocalStack — no real cloud access
- No user-facing authentication is needed for a single-developer local demo
- The `.env` file is gitignored

---

## Related Documents

- [Secrets Management](secrets-management.md)
- [Security Considerations](security-considerations.md)
