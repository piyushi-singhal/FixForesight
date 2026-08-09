# Requirements

## Functional Requirements

| ID | Requirement | Status |
|---|---|---|
| FR-01 | System shall ingest sensor telemetry from dataset CSV | ✅ Implemented |
| FR-02 | System shall perform feature engineering on raw telemetry | ✅ Implemented |
| FR-03 | System shall train a binary failure classification model | ✅ Implemented |
| FR-04 | System shall persist the trained model and scaler as artifacts | ✅ Implemented |
| FR-05 | System shall predict failure probability for each machine | ✅ Implemented |
| FR-06 | System shall classify failure type (heat_dissipation, tool_wear, overstrain, power_loss, random) | ✅ Implemented |
| FR-07 | System shall generate a prescriptive recommendation per prediction | ✅ Implemented |
| FR-08 | System shall persist machines, predictions, recommendations, alerts in PostgreSQL | ✅ Implemented |
| FR-09 | System shall expose REST API for all entities | ✅ Implemented |
| FR-10 | System shall provide a web dashboard displaying fleet health | ✅ Implemented |
| FR-11 | System shall support work order creation | ✅ Implemented |
| FR-12 | System shall support work order status transitions (open → in_progress → completed) | ✅ Implemented |
| FR-13 | System shall index predictions/recommendations in Solr for search | ✅ Implemented |
| FR-14 | System shall accept sensor events via SQS queue | ✅ Implemented (consumer thread) |
| FR-15 | System shall publish critical alerts via SNS topic | ✅ Implemented (infra configured) |
| FR-16 | System shall expose model feature importance | ✅ Implemented |
| FR-17 | System shall expose model evaluation metrics | 🟡 Partially (hardcoded values, not recalculated live) |

## Non-Functional Requirements

| ID | Requirement | Status |
|---|---|---|
| NFR-01 | Backend must start with database migration applied | ✅ Alembic upgrade head on startup |
| NFR-02 | Backend must handle Postgres unavailability with SQLite fallback | ✅ Implemented in connection.py |
| NFR-03 | All services must be containerised | ✅ Docker Compose |
| NFR-04 | Frontend must poll for live data without manual refresh | ✅ Redux polling intervals |
| NFR-05 | API must support CORS for local frontend | ✅ CORS middleware enabled |
| NFR-06 | System must not store secrets in code | 🟡 Partial — mock AWS keys hardcoded in docker-compose |
| NFR-07 | ML training and inference must use identical feature contract | ✅ Unified 5-feature contract |
| NFR-08 | Docker build must not require host-specific paths | 🟡 Partial — `data/` not copied into backend Docker image |

---

## Related Documents

- [Scope](scope.md)
- [Known Issues](../14-project-status/known-issues.md)
