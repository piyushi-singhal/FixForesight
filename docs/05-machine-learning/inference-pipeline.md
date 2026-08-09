# Inference Pipeline

## Overview

Runtime inference is implemented in `backend/services/db_service.predict_machine_failure()`.

---

## Function Signature

```python
def predict_machine_failure(air_temp, proc_temp, speed, torque, wear):
    -> (probability: float, predicted_failure: str, failure_type: str, time_to_failure: str)
```

## Execution Flow

```
1. Check if MODEL_AVAILABLE (best_model.pkl + scaler.pkl loaded at import time)

2. If Keras model present (best_model.h5 + TensorFlow installed):
     features = [[air_temp, proc_temp, speed, torque, wear]]
     features_scaled = scaler.transform(features)
     prob = model.predict(features_scaled)[0][0]

3. Else if scikit-learn model (best_model.pkl):
     n_features = scaler.n_features_in_
     if n_features == 5:
         features = [[air_temp, proc_temp, speed, torque, wear]]
     else:  # legacy 4-feature fallback
         temp_diff = air_temp - proc_temp
         features = [[torque, speed, temp_diff, wear]]
     features_scaled = scaler.transform(features)
     prob = model.predict_proba(features_scaled)[0][1]

4. If neither → rule-based fallback (no ML model):
     prob estimated from thresholds on torque, wear, speed, temp

5. Failure type classification (rule-based, independent of ML):
     if temp_diff < -15.0 or (proc_temp - air_temp) > 15.0:  → heat_dissipation
     elif wear > 180.0:                                        → tool_wear
     elif torque > 65.0:                                       → overstrain
     elif speed < 1200.0:                                      → power_loss
     else:                                                     → random_failure

6. Time-to-failure bucket:
     prob > 0.9  → "6 Hours"
     > 0.75      → "24 Hours"
     > 0.6       → "2 Days"
     > 0.5       → "5 Days"
     > 0.3       → "2 Weeks"
     else        → "1 Month"
```

---

## Model Loading (Module-Level)

In `db_service.py`, model loading happens at module import time:

```python
# Priority 1: Keras model (if TensorFlow installed)
keras_model_path = os.path.join(base_dir, "models", "best_model.h5")
# Priority 2: scikit-learn PKL model
pkl_model_path = os.path.join(base_dir, "models", "best_model.pkl")
scaler_path = os.path.join(base_dir, "models", "scaler.pkl")
```

The `base_dir` is computed dynamically from `__file__`, making it portable across environments.

---

## Legacy 4-Feature Fallback

The code contains a fallback for a 4-feature scaler:
```python
if n_features == 5:
    # Current canonical contract
    features = [[air_temp, proc_temp, speed, torque, wear]]
else:
    # Legacy contract: Torque, Speed, temp_diff, Tool_wear
    temp_diff = air_temp - proc_temp
    features = [[torque, speed, temp_diff, wear]]
```

> The current `models/scaler.pkl` uses 5 features. This branch exists for backward compatibility but should not be needed with the current artifacts.
