# Model Evaluation

## Evaluation Metrics

All metrics computed on the held-out 20% test set.

### Final Results (from `models/model_comparison.csv`)

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| **GradientBoosting** | **0.9845** | **0.8491** | 0.6618 | **0.7438** | **0.9618** |
| RandomForest | 0.9800 | 0.7121 | 0.6912 | 0.7015 | 0.9613 |
| LogisticRegression | 0.7475 | 0.1034 | 0.8382 | 0.1842 | 0.8490 |

### Interpretation

- **High Accuracy (98.45%)** — driven partly by class imbalance (~96.6% are non-failure)
- **Good Precision (84.9%)** — when the model predicts failure, it's correct ~85% of the time
- **Moderate Recall (66.2%)** — the model misses ~34% of true failures (false negatives)
- **Strong AUC (0.9618)** — excellent discrimination between failure and non-failure classes

### Practical Impact of 33.8% Miss Rate

In a maintenance context, missing a failure (false negative) is more costly than a false alarm (false positive). The current threshold of 0.5 can be lowered to improve recall at the cost of precision.

---

## Feature Importance (GradientBoosting)

Verified from `GET /analytics/feature-importance` endpoint using actual scikit-learn `feature_importances_`:

| Feature | Approx. Importance |
|---|---|
| `torque` | ~44% |
| `tool_wear` | ~17% |
| `rotational_speed` | ~13% |
| `process_temperature` | ~11% |
| `air_temperature` | ~15% |

> Note: Exact values vary by training run. The API returns live values from the loaded model.

---

## Model Monitoring Endpoint

`GET /analytics/model-monitoring` returns:
```json
{
  "accuracy": 0.9845,
  "precision": 0.885,
  "recall": 0.642,
  "f1": 0.7438,
  "roc_auc": 0.9618
}
```

> ⚠️ **Known Issue:** These are hardcoded values in `backend/routes/analytics.py`, not computed dynamically from live data. They match the training evaluation results but do not reflect model drift over time.
