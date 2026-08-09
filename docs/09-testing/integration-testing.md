# Integration Testing

## tests_integration.py

**Type:** Component-level tests (not full system integration)  
**Requirements:** Only `src/` modules — no database, no HTTP server needed

### Test 1 — Sensor Simulator (`test_sensor_simulator`)

Validates `src/sensor_simulator.py:SensorSimulator`:
- Normal operation data generation (100 samples)
- Failure scenarios: `heat_dissipation`, `power_loss`, `overstrain`, `tool_wear`
- Multi-machine dataset generation

### Test 2 — Feature Engineering (`test_feature_engineering`)

Validates `src/ml_pipeline.py:FeatureEngineer`:
- Temporal features: `hour`, `day_of_week`
- Sensor features: `temp_diff`, `power`, `wear_rate`
- Full pipeline produces more columns than input

### Test 3 — ML Model (`test_ml_model`)

Validates `src/ml_pipeline.py:PredictiveMaintenanceModel`:
- Trains on synthetic data
- Evaluates: accuracy, precision, recall, F1, AUC
- Makes predictions on test set

### Test 4 — Recommendation Engine (`test_recommendation_engine`)

Validates `src/recommendation_engine.py:RecommendationEngine`:
- Generates recommendations from prediction results

### Test 5 — Data Processing (`test_data_processing`)

Validates `src/data_pipeline.py:SensorDataProcessor`:
- Data cleaning
- Feature processing

---

## tests_api_e2e.py

**Type:** API end-to-end  
**Requirements:** Running backend at `http://127.0.0.1:8000` with PostgreSQL connected

Covers the critical ML → PostgreSQL → FastAPI flow:
1. Trigger prediction pipeline
2. Verify predictions in DB
3. Verify machines in DB
4. Create work order
5. Transition to in_progress
6. Transition to completed
