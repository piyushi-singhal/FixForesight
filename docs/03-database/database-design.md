# Database Design

## Overview

FixForesight uses **PostgreSQL 15** as the primary data store. The schema is defined in two places:

| Location | Purpose |
|---|---|
| `backend/db/schema.sql` | Docker init script — runs on first container start |
| `backend/database/models.py` | SQLAlchemy ORM models — source of truth at runtime |
| `backend/alembic/` | Alembic migrations — applied at every backend startup |

> **Source of Truth:** `backend/database/models.py` is authoritative. The SQL file matches it, but Alembic migrations are the runtime enforcement mechanism.

---

## Database: `pdm_db`

### Tables

| Table | Purpose | Rows at startup |
|---|---|---|
| `machines` | Current telemetry snapshot per machine | ~100 (from pipeline) |
| `predictions` | One failure prediction per machine per pipeline run | ~100 |
| `recommendations` | One maintenance recommendation per prediction | ~100 |
| `alerts` | SNS webhook alerts and system alerts | Variable |
| `work_orders` | Maintenance task lifecycle | User-created |
| `parts_inventory` | Spare parts stock tracking | Seed data |

---

## Connection Strategy

`backend/database/connection.py`:
1. Reads `DATABASE_URL` environment variable (default: `postgresql://postgres:postgres@localhost:5432/pdm_db`)
2. Attempts PostgreSQL connection (`pool_pre_ping=True`)
3. On failure: **automatic SQLite fallback** to `pdm_db.db` in project root
4. `SessionLocal` factory — used by all service functions

---

## Schema Consistency Note

The SQL `schema.sql` and ORM `models.py` are aligned on all columns. One discrepancy found:

- `schema.sql` comment says `-- TensorFlow output target` on the predictions table — this is outdated; actual runtime model is `GradientBoostingClassifier` (scikit-learn).

---

## Related Documents

- [Schema Reference](schema-reference.md)
- [Relationships](relationships.md)
- [Data Dictionary](data-dictionary.md)
- [ER Diagram](diagrams/er-diagram.mmd)
