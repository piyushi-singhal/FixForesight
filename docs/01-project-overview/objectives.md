# Objectives

## Primary Objectives

1. **Build an end-to-end ML pipeline** — from raw sensor data through feature engineering, model training, and serialized inference artifact — using scikit-learn.

2. **Implement a REST API backend** — FastAPI application exposing machines, predictions, recommendations, alerts, work orders, analytics, and search endpoints.

3. **Create a real-time dashboard** — React + Redux frontend displaying fleet health, machine telemetry, predictions, and maintenance workflows.

4. **Implement a prescriptive recommendation engine** — convert probabilistic failure predictions into prioritised, actionable maintenance instructions.

5. **Integrate cloud-native messaging infrastructure** — LocalStack-simulated SQS (event ingestion) and SNS (alert publishing), with FastAPI webhook receiver.

6. **Enable historical search** — Apache Solr indexing of incident data for full-text search across predictions and recommendations.

7. **Maintain database integrity** — PostgreSQL as the authoritative data store with SQLAlchemy ORM and Alembic-managed migrations.

8. **Support containerised deployment** — Docker Compose orchestrating all services: backend, frontend, PostgreSQL, LocalStack, and Solr.

---

## Secondary Objectives

- Demonstrate model explainability using scikit-learn feature importances.
- Provide model monitoring metrics (accuracy, precision, recall, F1, ROC-AUC).
- Support sensor simulation for testing without physical hardware.
- Implement work-order status lifecycle (open → in_progress → completed).

---

## Non-Objectives

- **Real-time streaming** at production scale — the current implementation is batch/file-based at the pipeline level.
- **Cloud deployment** — only LocalStack (local simulation) is configured; no actual AWS/GCP/Azure deployment exists.
- **Multi-tenant** — the system is designed for a single-tenant deployment.
- **Hardware integration** — no physical sensor SDK or OPC-UA protocol is implemented.

---

## Related Documents

- [Problem Statement](problem-statement.md)
- [Scope](scope.md)
