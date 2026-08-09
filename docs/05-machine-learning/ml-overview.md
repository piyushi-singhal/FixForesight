# Machine Learning Overview

## Purpose

The ML pipeline transforms raw sensor readings from industrial machines into a failure probability score, failure type classification, and estimated time to failure.

---

## What Is Actually Implemented

| Component | Status | Details |
|---|---|---|
| GradientBoostingClassifier | ✅ Trained & deployed | `models/best_model.pkl` — selected as production model |
| RandomForestClassifier | ✅ Trained | `models/random_forest_*.pkl` — comparison only |
| LSTM / Keras | 🟡 Code exists | In `src/ml_pipeline.py` but requires TensorFlow; **not trained** in current artifacts |
| 5-feature canonical contract | ✅ Enforced | air_temp, process_temp, rotational_speed, torque, tool_wear |
| RobustScaler | ✅ Deployed | `models/scaler.pkl` |

> **Important:** TensorFlow/Keras model types are present in the codebase but TensorFlow is NOT installed in the `.venv` environment. The runtime always falls back to scikit-learn `best_model.pkl`.

---

## Model Artifacts (Verified Present)

| Artifact | Size | Description |
|---|---|---|
| `models/best_model.pkl` | 800 KB | GradientBoostingClassifier (canonical production model) |
| `models/scaler.pkl` | 1 KB | RobustScaler fitted on training data |
| `models/gradient_boosting_20260623_204921.pkl` | 357 KB | Timestamped training run |
| `models/gradient_boosting_20260623_204930.pkl` | 357 KB | Timestamped training run |
| `models/random_forest_20260623_204921.pkl` | 1.8 MB | RandomForest training run |
| `models/random_forest_20260623_204930.pkl` | 1.8 MB | RandomForest training run |
| `models/*_features.json` | 85 B each | Feature list: 5 canonical features |
| `models/model_comparison.csv` | 302 B | Evaluation metrics comparison |

---

## Feature Contract (Training = Inference = Identical)

```python
feature_cols = [
    "air_temperature",
    "process_temperature",
    "rotational_speed",
    "torque",
    "tool_wear"
]
```

This is enforced in `src/ml_pipeline.py:PredictiveMaintenanceModel.prepare_data()` and matched in `backend/services/db_service.predict_machine_failure()`.

---

## Model Performance (from `models/model_comparison.csv`)

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| GradientBoosting | **0.9845** | **0.8491** | 0.6618 | **0.7438** | **0.9618** |
| RandomForest | 0.9800 | 0.7121 | 0.6912 | 0.7015 | 0.9613 |
| LogisticRegression | 0.7475 | 0.1034 | 0.8382 | 0.1842 | 0.8490 |

**Selection rationale:** GradientBoosting has the best Accuracy, Precision, F1, and AUC. RandomForest has marginally better Recall but at the cost of lower Precision.

---

## Related Documents

- [Preprocessing](preprocessing.md)
- [Feature Engineering](feature-engineering.md)
- [Model Training](model-training.md)
- [Model Evaluation](model-evaluation.md)
- [Inference Pipeline](inference-pipeline.md)
- [Recommendation Engine](recommendation-engine.md)
- [Model Artifacts](model-artifacts.md)
