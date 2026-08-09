# Preprocessing

## Raw Dataset Characteristics

**Dataset:** AI4I 2020 Predictive Maintenance Dataset  
**Source:** UCI Machine Learning Repository  
**File:** `data/FixForesightdataset.csv` (707 KB) / `data/ai4i2020_cleaned.csv` (513 KB)

| Property | Value |
|---|---|
| Rows | 10,000 |
| Failure rate | ~3.4% (340 failure rows) |
| Target column | `Machine failure` (binary: 0/1) |

## Original Column Names → Canonical Names

| Original Column | Canonical Name | Type |
|---|---|---|
| `Air temperature [K]` | `air_temperature` | Float (K) |
| `Process temperature [K]` | `process_temperature` | Float (K) |
| `Rotational speed [rpm]` | `rotational_speed` | Integer |
| `Torque [Nm]` | `torque` | Float (Nm) |
| `Tool wear [min]` | `tool_wear` | Float (min) |
| `Machine failure` | `failure` | Binary (0/1) |
| `UDI` | `UDI` | Integer (row index) |
| `Product ID` | `Product ID` | String (L/M/H prefix) |
| `Type` | `Type` | Categorical (L/M/H) |
| `TWF/HDF/PWF/OSF/RNF` | (sub-failure flags) | Binary (0/1) |

## Cleaning Steps (`src/clean_dataset.py`)

1. Rename columns to canonical snake_case names
2. Drop null rows
3. Drop duplicate rows
4. Output: `data/ai4i2020_cleaned.csv`

## Scaling

`RobustScaler` is applied during training and saved to `models/scaler.pkl`.

```python
# Robust to outliers — uses median/IQR
self.scaler = RobustScaler()
X_scaled = self.scaler.fit_transform(X)
```

At inference time, the same scaler is loaded and applied via `scaler.transform(features)`.
