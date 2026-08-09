# Project Overview

## FixForesight

**FixForesight** is an end-to-end predictive and prescriptive maintenance platform for industrial machinery. It transforms raw sensor telemetry into actionable maintenance intelligence — predicting failures before they occur and prescribing specific corrective actions to minimize downtime.

---

## Purpose

Industrial equipment failure is costly and often preventable. FixForesight sits between raw sensor data and maintenance teams, providing:

- **Failure prediction** — ML inference on live telemetry to compute failure probability per machine.
- **Prescriptive recommendations** — Rule-based engine converting predictions into prioritised maintenance actions.
- **Work-order management** — Digital workflow from alert to completion, tracked in the database.
- **Fleet dashboard** — Real-time visibility into machine health across the entire fleet.
- **Search** — Apache Solr-backed full-text search over historical incidents and alerts.

---

## Domain Context

The system is designed around the AI4I 2020 Predictive Maintenance Dataset (UCI ML Repository), which models realistic industrial machine behaviour including:

| Failure Mode | Description |
|---|---|
| Tool Wear Failure | Cumulative wear exceeding 200–240 min threshold |
| Heat Dissipation Failure | Temperature differential outside operating range |
| Overstrain Failure | Torque × RPM product exceeding mechanical limit |
| Power Loss Failure | Rotational speed drop below operational minimum |
| Random Failure | Stochastic faults (< 0.1% base rate) |

---

## System at a Glance

```
Sensor Telemetry / CSV Dataset
         ↓
Feature Engineering (src/feature_engineering_pipeline.py)
         ↓
ML Inference — GradientBoostingClassifier (models/best_model.pkl)
         ↓
Failure Probability + Failure Type + Time-to-Failure
         ↓
Recommendation Engine (src/recommendation_engine.py)
         ↓
PostgreSQL  ←—→  FastAPI (backend/main.py)
         ↓
React + Redux Dashboard (frontend/)
```

---

## Related Documents

- [Problem Statement](problem-statement.md)
- [Objectives](objectives.md)
- [Scope](scope.md)
- [Requirements](requirements.md)
