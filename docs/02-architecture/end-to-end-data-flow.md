# End-to-End Data Flow

## Overview

This document traces data from raw sensor readings through every system layer to the end-user dashboard.

---

## Stage-by-Stage Flow

### Stage 1 — Raw Data

| File | Description |
|---|---|
| `data/FixForesightdataset.csv` | Original AI4I 2020 dataset (10,000 rows) |
| `data/ai4i2020_cleaned.csv` | After `src/clean_dataset.py` — same as FixForesight-cleaneddataset.csv |
| `data/engineered_ai4i.csv` | After `src/feature_engineering_pipeline.py` — 15+ columns |
| `data/processed_features.csv` | Output of `src/data_pipeline.py` |

**Column mapping from original → canonical:**
```
Air temperature [K]       → air_temperature
Process temperature [K]   → process_temperature
Rotational speed [rpm]    → rotational_speed
Torque [Nm]               → torque
Tool wear [min]            → tool_wear
Machine failure           → failure
```

---

### Stage 2 — Feature Engineering

**Module:** `src/feature_engineering_pipeline.py`, `src/ml_pipeline.py:FeatureEngineer`

Engineered features created (from raw telemetry):

| Feature | Formula | Used in Inference? |
|---|---|---|
| `temp_diff` | process_temp - air_temp | No (inference uses raw 5) |
| `temp_ratio` | process_temp / air_temp | No |
| `power` | rotational_speed × torque | No |
| `wear_rate` | tool_wear / rotational_speed | No |
| `thermal_stress` | normalised process_temp | No |
| `mechanical_stress` | normalised torque × speed | No |

> **Important:** The ML inference pipeline uses only the 5 raw features. The additional engineered features are produced during exploratory training but the `best_model.pkl` was trained on the 5-feature contract.

---

### Stage 3 — ML Training

**Module:** `src/ml_pipeline.py:PredictiveMaintenanceModel`

1. Load `data/engineered_ai4i.csv` (or fallback to cleaned CSV)
2. Select 5 features: `[air_temperature, process_temperature, rotational_speed, torque, tool_wear]`
3. `RobustScaler.fit_transform()` → save to `models/scaler.pkl`
4. 80/20 stratified train/test split
5. Train `GradientBoostingClassifier` and `RandomForestClassifier`
6. Evaluate both; GradientBoosting selected (Acc=98.45%, AUC=0.9618)
7. Save to `models/best_model.pkl` (GradientBoosting copy)

---

### Stage 4 — Startup Inference Pipeline

**Module:** `backend/main.py:startup_pipeline()` → `backend/services/db_service.run_predictions_pipeline()`

1. Check `tmp/pipeline.lock` — skip if already run this process
2. Load `data/engineered_ai4i.csv`
3. Clear `machines`, `predictions`, `recommendations` tables
4. For each row (up to `limit=100`):
   - Generate `machine_id = M{100 + UDI}`
   - Call `predict_machine_failure(air_temp, proc_temp, speed, torque, wear)`
   - Determine `status` (Healthy / Warning / Critical)
   - Insert `Machine`, `Prediction`, `Recommendation` rows
5. Commit to PostgreSQL
6. Sync to Solr

---

### Stage 5 — ML Inference Function

**Module:** `backend/services/db_service.predict_machine_failure()`

```
Input: air_temp, proc_temp, speed, torque, wear
  ↓
features = np.array([[air_temp, proc_temp, speed, torque, wear]])
  ↓
features_scaled = scaler.transform(features)
  ↓
prob = best_model.predict_proba(features_scaled)[0][1]
  ↓
failure_type = rule-based classification (temp_diff, wear, torque, speed thresholds)
  ↓
time_to_failure = bucketed estimate (6h / 24h / 2d / 5d / 2w / 1m)
  ↓
Output: (probability, predicted_failure_label, failure_type, time_to_failure)
```

---

### Stage 6 — Recommendation Engine

**Module:** `src/recommendation_engine.py:RecommendationEngine`

Rule-based thresholds in `predictions_pipeline.py`:
- `prob > 0.8` → "Immediate Maintenance Required", priority=Critical
- `prob > 0.5` → "Schedule preventive maintenance", priority=Medium
- else → "No active recommendations", priority=Low

---

### Stage 7 — PostgreSQL Storage

Tables written per machine iteration:
- `machines` — telemetry snapshot + status
- `predictions` — failure_probability × 100, predicted_failure, time_to_failure
- `recommendations` — text, priority, confidence (prob × 100)

---

### Stage 8 — API Layer

FastAPI routes query PostgreSQL via SQLAlchemy ORM (`SessionLocal`).

Key query patterns in `backend/database/queries.py` and `backend/services/db_service.py`:
- `get_all_machines()` — JOIN machines + latest prediction + recommendation
- `get_all_predictions()` — JOIN predictions + machine telemetry
- `search_incidents(q)` — Solr `select?q={q}` HTTP call

---

### Stage 9 — Frontend Rendering

React components poll the API at configured intervals (Redux Toolkit `createAsyncThunk`).

Data path: `apiConfig.js (BASE_URL) → *Service.ts → store/*Slice.ts → App.jsx`

---

## Diagram

See [data-flow.mmd](diagrams/data-flow.mmd) for the Mermaid flowchart.
