# Dataset

## AI4I 2020 Predictive Maintenance Dataset

**Source:** UCI Machine Learning Repository  
**Full name:** AI4I 2020 Predictive Maintenance Dataset  
**Rows:** 10,000  
**Failure rate:** ~3.4% (340 failure rows)

---

## Original Columns

| Column | Type | Description |
|---|---|---|
| `UDI` | int | Row index (1–10,000) |
| `Product ID` | string | Product type + serial (L/M/H prefix) |
| `Type` | string | Quality type: L (low), M (medium), H (high) |
| `Air temperature [K]` | float | Ambient temperature in Kelvin |
| `Process temperature [K]` | float | Process temperature in Kelvin |
| `Rotational speed [rpm]` | int | Motor rotational speed |
| `Torque [Nm]` | float | Motor torque |
| `Tool wear [min]` | float | Cumulative tool wear time |
| `Machine failure` | int | Binary: 1 = failure, 0 = no failure |
| `TWF` | int | Tool Wear Failure sub-label |
| `HDF` | int | Heat Dissipation Failure sub-label |
| `PWF` | int | Power Failure sub-label |
| `OSF` | int | Overstrain Failure sub-label |
| `RNF` | int | Random Failure sub-label |

---

## Files in Repository

| File | Description |
|---|---|
| `data/FixForesightdataset.csv` | Original dataset (707 KB) |
| `data/FixForesight-cleaneddataset.csv` | Cleaned version (513 KB) |
| `data/ai4i2020_cleaned.csv` | Cleaned version (same as above, 513 KB) |
| `data/engineered_ai4i.csv` | After feature engineering (978 KB) |
| `data/processed_features.csv` | After data_pipeline.py processing (673 KB) |

---

## Class Distribution

| Class | Count | Percentage |
|---|---|---|
| No failure (0) | ~9,660 | ~96.6% |
| Failure (1) | ~340 | ~3.4% |

This class imbalance affects model training. The current implementation uses stratified split but no explicit oversampling.
