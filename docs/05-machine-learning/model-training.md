# Model Training

## Entry Points

| Script | Purpose |
|---|---|
| `src/ml_pipeline.py` | `PredictiveMaintenanceModel` class — training and evaluation |
| `models/train_models.py` | Standalone training entry-point (separate from main pipeline) |
| `src/ml_pipeline.py:main()` | Demo training run |

---

## Training Process

### 1. Data Loading

```python
data_path = Path("data/engineered_ai4i.csv")
# Fallback: data/ai4i2020_cleaned.csv
df = pd.read_csv(data_path)
```

### 2. Column Mapping

Original dataset columns renamed to canonical names:
```python
mapping = {
    "Air temperature [K]": "air_temperature",
    "Process temperature [K]": "process_temperature",
    "Rotational speed [rpm]": "rotational_speed",
    "Torque [Nm]": "torque",
    "Tool wear [min]": "tool_wear",
    "Machine failure": "failure"
}
```

### 3. Feature Selection (Hard-coded 5-feature contract)

```python
feature_cols = [
    "air_temperature",
    "process_temperature",
    "rotational_speed",
    "torque",
    "tool_wear"
]
```

### 4. Scaling

`RobustScaler` — robust to outliers (uses median and IQR instead of mean/std).

```python
self.scaler = RobustScaler()
X_scaled = self.scaler.fit_transform(X)
```

### 5. Train/Test Split

```python
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)
```

Stratified split ensures class balance is maintained (important given ~3.4% failure rate).

### 6. Model Configurations

**GradientBoostingClassifier:**
```python
GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42
)
```

**RandomForestClassifier:**
```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
```

### 7. Serialization

```python
# Model saved with timestamp
models/gradient_boosting_YYYYMMDD_HHMMSS.pkl
models/gradient_boosting_YYYYMMDD_HHMMSS_scaler.pkl
models/gradient_boosting_YYYYMMDD_HHMMSS_features.json

# Best model copied to canonical path
models/best_model.pkl  ← GradientBoosting copy
models/scaler.pkl      ← corresponding scaler
```

---

## Class Imbalance

The dataset has ~3.4% failure rate (Machine failure = 1). The stratified split preserves this ratio. No explicit SMOTE or class weighting was applied in the current implementation.

This contributes to the model's high Accuracy (majority class dominates) but moderate Recall (0.66) — the model misses ~34% of actual failures.

---

## Training Logs

See `training_output.log` in the project root for detailed output from the last training run.
