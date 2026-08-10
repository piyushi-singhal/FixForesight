# tests/test_ml.py
"""
Unit tests for Machine Learning model properties:
- Model artifact loading
- Feature ordering verification
- Scaler compatibility checks
- Prediction range validation
"""

import os
import sys
import joblib
import numpy as np
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def test_model_artifact_loading():
    """Verify that ML models and scaler artifacts exist and load correctly."""
    pkl_model_path = PROJECT_ROOT / "models" / "best_model.pkl"
    scaler_path = PROJECT_ROOT / "models" / "scaler.pkl"

    assert pkl_model_path.exists(), f"Model pkl missing at {pkl_model_path}"
    assert scaler_path.exists(), f"Scaler pkl missing at {scaler_path}"

    # Load artifacts
    model = joblib.load(pkl_model_path)
    scaler = joblib.load(scaler_path)

    assert model is not None
    assert scaler is not None

def test_feature_ordering():
    """Verify that feature contract uses the exact 5 canonical features in sequence."""
    scaler_path = PROJECT_ROOT / "models" / "scaler.pkl"
    scaler = joblib.load(scaler_path)
    
    expected_features = [
        "air_temperature",
        "process_temperature",
        "rotational_speed",
        "torque",
        "tool_wear"
    ]
    
    if hasattr(scaler, "feature_names_in_"):
        features = scaler.feature_names_in_.tolist()
        assert features == expected_features, f"Feature mismatch. Expected: {expected_features}, Got: {features}"
    else:
        # Fallback to verify shape matches
        assert scaler.n_features_in_ == len(expected_features)


def test_scaler_compatibility():
    """Verify that inputs passed to the scaler yield compatible transformed shapes."""
    scaler_path = PROJECT_ROOT / "models" / "scaler.pkl"
    scaler = joblib.load(scaler_path)

    # 5 features input
    test_input = np.array([[298.1, 308.6, 1500, 40.0, 50.0]])
    scaled_input = scaler.transform(test_input)
    assert scaled_input.shape == (1, 5)

def test_prediction_range():
    """Verify that predictions yield probabilities strictly within valid probability bounds [0.0, 1.0]."""
    pkl_model_path = PROJECT_ROOT / "models" / "best_model.pkl"
    scaler_path = PROJECT_ROOT / "models" / "scaler.pkl"
    
    model = joblib.load(pkl_model_path)
    scaler = joblib.load(scaler_path)

    # Test cases: normal and extreme values
    test_inputs = np.array([
        [298.1, 308.6, 1500, 40.0, 50.0],  # Normal
        [304.5, 315.8, 2350, 68.2, 195.0]  # Degradation / failure state
    ])
    scaled_inputs = scaler.transform(test_inputs)
    
    # Predict failure probability
    probs = model.predict_proba(scaled_inputs)[:, 1]
    
    for prob in probs:
        assert 0.0 <= prob <= 1.0, f"Failure probability {prob} out of bounds"
