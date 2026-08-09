# FixForesight Documentation

> **The codebase is the source of truth.** This documentation is derived from direct inspection of the actual source files, configuration, and model artifacts as they exist in the repository.

## Welcome

**FixForesight** is a predictive and prescriptive maintenance system for industrial machinery. It ingests sensor telemetry, runs machine-learning inference to predict equipment failures, generates maintenance recommendations, and delivers results through a REST API and browser dashboard.

---

## Documentation Map

| Section | Contents |
|---------|----------|
| [01 – Project Overview](01-project-overview/project-overview.md) | Purpose, problem, objectives, scope |
| [02 – Architecture](02-architecture/system-architecture.md) | System design, data flow, deployment, sequence flows |
| [03 – Database](03-database/database-design.md) | Schema, ER diagram, data dictionary, relationships |
| [04 – Data Engineering](04-data-engineering/data-pipeline.md) | Dataset, sensor simulator, cleaning, feature engineering |
| [05 – Machine Learning](05-machine-learning/ml-overview.md) | Pipeline, training, evaluation, inference, artifacts |
| [06 – Backend](06-backend/backend-architecture.md) | FastAPI, all routes, contracts, error handling |
| [07 – Frontend](07-frontend/frontend-architecture.md) | React app, Redux, pages, API integration |
| [08 – Infrastructure](08-infrastructure/docker.md) | Docker, docker-compose, LocalStack, SQS/SNS, Solr |
| [09 – Testing](09-testing/testing-strategy.md) | Strategy, test classification, validation checklist |
| [10 – Deployment](10-deployment/local-setup.md) | Local setup, Docker deployment, environment config |
| [11 – Security](11-security/security-overview.md) | Security practices, known gaps |
| [12 – Architecture Decisions](12-architecture-decisions/architecture-decision-records.md) | Why each technology was chosen |
| [13 – Troubleshooting](13-troubleshooting/troubleshooting.md) | Common problems and solutions |
| [14 – Project Status](14-project-status/current-status.md) | Honest status, known issues, roadmap |

---

## Quick Links

- [API Reference](06-backend/api-reference.md)
- [ER Diagram](03-database/diagrams/er-diagram.mmd)
- [System Architecture Diagram](02-architecture/diagrams/system-architecture.mmd)
- [ML Pipeline Diagram](02-architecture/diagrams/ml-pipeline.mmd)
- [Current Status & Known Issues](14-project-status/known-issues.md)
- [Deployment Guide](10-deployment/docker-deployment.md)

---

*Last updated: August 2026 — Verified against repository commit state.*
