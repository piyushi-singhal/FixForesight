# Apache Solr

## Purpose

Apache Solr provides full-text search over historical incident data (predictions and recommendations).

**Image:** `solr:9-alpine`  
**Port:** `8983` (Admin UI: `http://localhost:8983/solr`)  
**Core:** `incidents`

---

## Setup

The `incidents` core is auto-created via the Docker command:
```
command: solr-precreate incidents
```

No custom schema configuration is applied — Solr uses its default managed schema (schemaless mode).

---

## Data Synchronization

`backend/services/db_service.sync_data_to_solr()` runs:
1. On every backend startup (after prediction pipeline)
2. After each pipeline run (`POST /predictions/pipeline`)

It queries PostgreSQL for predictions and recommendations, then POSTs documents to Solr.

---

## Search API

```
GET /search?q={query}
```

The backend calls:
```python
requests.get(f"{SOLR_URL}/select?q={q}&wt=json")
```

`SOLR_URL` defaults to `http://localhost:8983/solr/incidents`.

---

## Fallback Behavior

If Solr is unreachable, `search_incidents()` catches the exception and returns an empty list. The backend logs a warning but does not crash.

---

## Known Issues

1. **No schema definition** — uses Solr managed schema. Field types are inferred from first-document field values. This can cause type inconsistencies.
2. **No authentication** — Solr admin UI is open with no credentials.
3. **Data volume** — Solr is re-synced on every startup, replacing previous data. No incremental indexing.
