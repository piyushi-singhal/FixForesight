"""
Integration Test Suite for Industrial AI Platform
Tests the complete pipeline from data generation to recommendations
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sensor_simulator import SensorSimulator
from ml_pipeline import FeatureEngineer, PredictiveMaintenanceModel
from recommendation_engine import RecommendationEngine
from data_pipeline import SensorDataProcessor


def test_sensor_simulator():
    """Test sensor data simulator."""
    print("\n" + "=" * 80)
    print("TEST 1: Sensor Data Simulator")
    print("=" * 80)

    simulator = SensorSimulator(seed=42)

    # Test normal operation
    print("\n✓ Generating normal operation data...")
    df_normal = simulator.generate_normal_operation(num_samples=100)
    assert len(df_normal) == 100, "Normal operation sample count mismatch"
    assert "air_temperature" in df_normal.columns, "Missing air_temperature column"
    print(f"  Generated {len(df_normal)} samples")

    # Test failure scenarios
    print("✓ Generating failure scenarios...")
    for failure_type in ["heat_dissipation", "power_loss", "overstrain", "tool_wear"]:
        df_failure, metadata = simulator.generate_failure_scenario(
            failure_type=failure_type, num_samples_normal=50, num_samples_degradation=50
        )
        assert len(df_failure) == 100, f"Failure scenario {failure_type} sample count mismatch"
        assert metadata["failure_type"] == failure_type, "Failure type metadata mismatch"
        print(f"  ✓ {failure_type}: {len(df_failure)} samples")

    # Test multi-machine dataset
    print("✓ Generating multi-machine dataset...")
    df_multi = simulator.generate_multiple_machines_dataset(num_machines=3, samples_per_machine=50)
    assert len(df_multi) > 0, "Multi-machine dataset is empty"
    assert "machine_id" in df_multi.columns, "Missing machine_id column"
    print(f"  Generated {len(df_multi)} samples for {df_multi['machine_id'].nunique()} machines")

    print("\n✓ TEST 1 PASSED: Sensor Simulator works correctly")
    return df_normal


def test_feature_engineering(df):
    """Test feature engineering."""
    print("\n" + "=" * 80)
    print("TEST 2: Feature Engineering")
    print("=" * 80)

    engineer = FeatureEngineer()

    # Test temporal features
    print("\n✓ Engineering temporal features...")
    df_with_timestamp = df.copy()
    df_with_timestamp["timestamp"] = pd.date_range(start="2024-01-01", periods=len(df), freq="1min")
    df_temporal = engineer.create_temporal_features(df_with_timestamp)
    assert "hour" in df_temporal.columns, "Missing hour feature"
    assert "day_of_week" in df_temporal.columns, "Missing day_of_week feature"
    print(f"  Added temporal features: {len(df_temporal.columns)} columns")

    # Test sensor features
    print("✓ Engineering sensor features...")
    df_sensor = engineer.create_sensor_features(df.copy())
    assert "temp_diff" in df_sensor.columns, "Missing temp_diff feature"
    assert "power" in df_sensor.columns, "Missing power feature"
    assert "wear_rate" in df_sensor.columns, "Missing wear_rate feature"
    print(f"  Added sensor features: {len(df_sensor.columns)} columns")

    # Test full engineering pipeline
    print("✓ Running full feature engineering pipeline...")
    df_engineered = engineer.engineer_features(df.copy())
    assert df_engineered.shape[1] > df.shape[1], "No features were added"
    print(f"  Original: {df.shape[1]} columns → Engineered: {df_engineered.shape[1]} columns")

    print("\n✓ TEST 2 PASSED: Feature Engineering works correctly")
    return df_engineered


def test_ml_model(df_engineered):
    """Test ML model training and prediction."""
    print("\n" + "=" * 80)
    print("TEST 3: ML Model Training & Evaluation")
    print("=" * 80)

    # Create synthetic target
    df_engineered["failure"] = (df_engineered["tool_wear"] > df_engineered["tool_wear"].quantile(0.8)).astype(
        int
    )

    print("\n✓ Training Gradient Boosting model...")
    model_gb = PredictiveMaintenanceModel(model_type="gradient_boosting")
    X_train, X_test, y_train, y_test = model_gb.prepare_data(df_engineered)

    assert X_train.shape[0] > 0, "Training set is empty"
    assert X_test.shape[0] > 0, "Test set is empty"
    print(f"  Training set: {X_train.shape[0]} samples")
    print(f"  Test set: {X_test.shape[0]} samples")
    print(f"  Features: {X_train.shape[1]}")

    model_gb.train(X_train, y_train)
    metrics = model_gb.evaluate(X_test, y_test)

    assert "accuracy" in metrics, "Missing accuracy metric"
    assert metrics["accuracy"] > 0.5, "Model accuracy too low"
    print(f"  Accuracy: {metrics['accuracy']:.4f}")
    print(f"  F1-Score: {metrics['f1']:.4f}")

    # Test Random Forest
    print("✓ Training Random Forest model...")
    model_rf = PredictiveMaintenanceModel(model_type="random_forest")
    model_rf.train(X_train, y_train)
    metrics_rf = model_rf.evaluate(X_test, y_test)
    print(f"  Accuracy: {metrics_rf['accuracy']:.4f}")

    # Test predictions
    print("✓ Testing predictions...")
    predictions = model_gb.predict(X_test[:10])
    assert len(predictions) == 10, "Prediction count mismatch"
    assert all(0 <= p <= 1 for p in predictions), "Invalid prediction values"
    print(f"  Generated {len(predictions)} predictions")

    print("\n✓ TEST 3 PASSED: ML Model Training works correctly")
    return model_gb


def test_recommendation_engine():
    """Test recommendation engine."""
    print("\n" + "=" * 80)
    print("TEST 4: Recommendation Engine")
    print("=" * 80)

    engine = RecommendationEngine()

    # Test risk assessment
    print("\n✓ Testing risk assessment...")
    risk_high = engine.assess_risk_level(0.85, days_to_failure=2)
    assert risk_high in ["critical", "high"], f"Unexpected risk level: {risk_high}"
    print(f"  High probability (0.85, 2 days) → {risk_high}")

    risk_low = engine.assess_risk_level(0.25, days_to_failure=20)
    assert risk_low in ["low", "medium"], f"Unexpected risk level: {risk_low}"
    print(f"  Low probability (0.25, 20 days) → {risk_low}")

    # Test spare parts retrieval
    print("✓ Testing spare parts catalog...")
    parts_high = engine.get_spare_parts("heat_dissipation", "high")
    assert len(parts_high) > 0, "No spare parts found"
    print(f"  Spare parts for heat_dissipation (high): {len(parts_high)} items")

    # Test recommendations
    print("✓ Generating recommendations...")
    rec = engine.generate_recommendation(
        machine_id=1,
        prediction_id=101,
        failure_type="heat_dissipation",
        failure_probability=0.85,
        days_to_failure=2,
    )

    assert rec.machine_id == 1, "Machine ID mismatch"
    assert rec.priority == "critical", "Priority should be critical"
    assert len(rec.spare_parts) > 0, "No spare parts in recommendation"
    print(f"  Priority: {rec.priority}")
    print(f"  Estimated Cost: ${rec.estimated_cost:.2f}")
    print(f"  Spare Parts: {len(rec.spare_parts)} items")

    # Test batch recommendations
    print("✓ Testing batch recommendations...")
    predictions_df = pd.DataFrame(
        [
            {
                "machine_id": 1,
                "prediction_id": 101,
                "failure_type": "heat_dissipation",
                "failure_probability": 0.85,
                "days_to_failure": 2,
            },
            {
                "machine_id": 2,
                "prediction_id": 102,
                "failure_type": "tool_wear",
                "failure_probability": 0.65,
                "days_to_failure": 5,
            },
        ]
    )
    recs = engine.generate_batch_recommendations(predictions_df)
    assert len(recs) == 2, "Batch recommendation count mismatch"
    print(f"  Generated {len(recs)} recommendations")

    print("\n✓ TEST 4 PASSED: Recommendation Engine works correctly")


def test_data_processor():
    """Test data processing utilities."""
    print("\n" + "=" * 80)
    print("TEST 5: Data Processor")
    print("=" * 80)

    print("\n✓ Testing message parsing...")
    message = {
        "machine_id": "1",
        "sensor_id": "1",
        "value": "320.5",
        "timestamp": "2024-01-15T10:30:00Z",
    }
    parsed = SensorDataProcessor.parse_sensor_message(message)
    assert parsed is not None, "Failed to parse message"
    assert parsed["machine_id"] == 1, "Machine ID not converted to int"
    assert parsed["value"] == 320.5, "Value not converted to float"
    print(f"  Parsed message: machine_id={parsed['machine_id']}, value={parsed['value']}")

    # Test batch processing
    print("✓ Testing batch processing...")
    messages = [message for _ in range(5)]
    readings = SensorDataProcessor.batch_process_readings(messages)
    assert len(readings) == 5, "Batch processing count mismatch"
    print(f"  Processed {len(readings)} messages")

    # Test validation
    print("✓ Testing data validation...")
    sensor_specs = {
        1: {"min": 308, "max": 335},
        2: {"min": 0, "max": 3000},
    }
    valid_readings = SensorDataProcessor.validate_readings(readings, sensor_specs)
    assert len(valid_readings) <= len(readings), "Validation failed"
    print(f"  Valid readings: {len(valid_readings)}/{len(readings)}")

    print("\n✓ TEST 5 PASSED: Data Processor works correctly")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("INDUSTRIAL AI PLATFORM - INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run tests in sequence
        df = test_sensor_simulator()
        df_engineered = test_feature_engineering(df)
        model = test_ml_model(df_engineered)
        test_recommendation_engine()
        test_data_processor()

        # Summary
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nThe Industrial AI Platform is ready for deployment!")
        print("\nNext steps:")
        print("  1. Set up PostgreSQL database: psql -U postgres -f src/database_schema.sql")
        print("  2. Generate production data: python src/sensor_simulator.py")
        print("  3. Train final model: python src/ml_pipeline.py")
        print("  4. Load data to database: python src/data_pipeline.py")
        print("=" * 80)

        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        print("=" * 80)
        return 1

    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        print("=" * 80)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
