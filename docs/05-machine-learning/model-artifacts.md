# Model Artifacts

## Production Artifacts (Used at Runtime)

| File | Size | Description |
|---|---|---|
| `models/best_model.pkl` | ~800 KB | GradientBoostingClassifier — production model |
| `models/scaler.pkl` | ~1 KB | RobustScaler — fitted on 5 canonical features |

These two files are loaded by `backend/services/db_service.py` at module import time.

---

## Training Run Artifacts

Timestamped artifacts from training runs on 2026-06-23:

| File | Description |
|---|---|
| `models/gradient_boosting_20260623_204921.pkl` | GradientBoosting run 1 |
| `models/gradient_boosting_20260623_204921_scaler.pkl` | Scaler for run 1 |
| `models/gradient_boosting_20260623_204921_features.json` | Features: 5 canonical |
| `models/gradient_boosting_20260623_204930.pkl` | GradientBoosting run 2 |
| `models/gradient_boosting_20260623_204930_scaler.pkl` | Scaler for run 2 |
| `models/random_forest_20260623_204921.pkl` | RandomForest run 1 |
| `models/random_forest_20260623_204921_scaler.pkl` | Scaler for run 1 |
| `models/random_forest_20260623_204930.pkl` | RandomForest run 2 |
| `models/random_forest_20260623_204930_scaler.pkl` | Scaler for run 2 |
| `models/model_comparison.csv` | Evaluation metrics for all models |

---

## Feature Contract (All Artifacts)

All `*_features.json` files contain:
```json
["air_temperature", "process_temperature", "rotational_speed", "torque", "tool_wear"]
```

---

## Deprecated / Not Used

| File | Notes |
|---|---|
| `models/selected_features.pkl` | Legacy artifact from an older 4-feature contract. Not used by current inference code. |
| `models/gradient_boosting_20260623_204930*.pkl` | Duplicate training run; `best_model.pkl` is authoritative |

---

## Docker Deployment Note

`backend/Dockerfile` copies `models/` into the Docker image at `/app/models/`. The production artifacts (`best_model.pkl`, `scaler.pkl`) are included.
