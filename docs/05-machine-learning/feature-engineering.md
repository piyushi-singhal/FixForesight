# Feature Engineering

## Overview

Feature engineering is implemented in two modules:
- `src/ml_pipeline.py:FeatureEngineer` — used during training exploration
- `src/feature_engineering_pipeline.py` — full pipeline for producing `data/engineered_ai4i.csv`

---

## Engineered Features

These features are computed during dataset preparation:

| Feature | Formula | Purpose |
|---|---|---|
| `temp_diff` | `process_temperature - air_temperature` | Detect heat dissipation issues |
| `temp_ratio` | `process_temperature / air_temperature` | Relative thermal load |
| `power` | `rotational_speed × torque` | Mechanical power |
| `power_normalized` | `power / max(power)` | Scaled power |
| `wear_rate` | `tool_wear / (rotational_speed + ε)` | Tool wear per RPM |
| `thermal_stress` | min-max normalized `process_temperature` | Thermal load index |
| `mechanical_stress` | min-max normalized `torque × speed` | Mechanical load index |
| `hour` | from timestamp | Hour of day |
| `day_of_week` | from timestamp | Day of week |
| `day_of_month` | from timestamp | Day of month |
| `vibration_energy` | `vibration²` | Vibration intensity |

---

## Important: Engineered Features vs. Inference Features

> The additional engineered features above are produced in `data/engineered_ai4i.csv` but **are NOT used by the production inference model**.

The model (`best_model.pkl`) was trained on exactly **5 raw features**:

```python
["air_temperature", "process_temperature", "rotational_speed", "torque", "tool_wear"]
```

The engineered features (`temp_diff`, `power`, etc.) were part of the exploratory phase but were not included in the final 5-feature contract.

This means the engineered CSV has additional columns that the model ignores at inference time.
