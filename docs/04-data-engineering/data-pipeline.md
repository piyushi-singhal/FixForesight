# Data Pipeline

## Overview

The data pipeline transforms the raw AI4I 2020 dataset through cleaning and feature engineering into a model-ready CSV.

---

## Pipeline Stages

```
data/FixForesightdataset.csv        (raw, 10,000 rows)
           ↓ src/clean_dataset.py
data/ai4i2020_cleaned.csv           (cleaned, same structure)
           ↓ src/feature_engineering_pipeline.py
data/engineered_ai4i.csv            (engineered, ~15+ columns)
           ↓ src/predictions_pipeline.py
PostgreSQL machines + predictions + recommendations
```

---

## Files

| File | Module | Purpose |
|---|---|---|
| `data/FixForesightdataset.csv` | — | Raw dataset (707 KB) |
| `data/ai4i2020_cleaned.csv` | `src/clean_dataset.py` | After cleaning |
| `data/engineered_ai4i.csv` | `src/feature_engineering_pipeline.py` | After feature engineering |
| `data/processed_features.csv` | `src/data_pipeline.py` | Alternative processed output |
| `src/data_pipeline.py` | `SensorDataProcessor` class | Data processing utilities |

---

## Running the Pipeline

```bash
# Step 1: Clean
cd src
python clean_dataset.py

# Step 2: Feature engineering
python feature_engineering_pipeline.py

# Step 3: Load into DB (via backend startup or direct script)
python predictions_pipeline.py
```

---

## Related Documents

- [Dataset](dataset.md)
- [Sensor Simulation](sensor-simulation.md)
- [Data Cleaning](data-cleaning.md)
- [Feature Engineering](feature-engineering.md)
