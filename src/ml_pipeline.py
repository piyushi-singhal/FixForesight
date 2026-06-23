"""
Industrial AI Platform - Feature Engineering & Model Training
Comprehensive ML pipeline for predictive maintenance
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
)
HAS_TENSORFLOW = False
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    HAS_TENSORFLOW = True
except ImportError:
    pass
import pickle
import json
from pathlib import Path
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


class FeatureEngineer:
    """Engineer features from raw sensor data."""

    @staticmethod
    def create_temporal_features(df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.DataFrame:
        """Extract temporal features from timestamp."""
        if timestamp_col in df.columns:
            df[timestamp_col] = pd.to_datetime(df[timestamp_col])
            df["hour"] = df[timestamp_col].dt.hour
            df["day_of_week"] = df[timestamp_col].dt.dayofweek
            df["day_of_month"] = df[timestamp_col].dt.day
        return df

    @staticmethod
    def create_sensor_features(df: pd.DataFrame) -> pd.DataFrame:
        """Create engineered features from raw sensor values."""
        # Temperature difference
        if "air_temperature" in df.columns and "process_temperature" in df.columns:
            df["temp_diff"] = df["process_temperature"] - df["air_temperature"]
            df["temp_ratio"] = df["process_temperature"] / df["air_temperature"]

        # Power calculation (RPM * Torque)
        if "rotational_speed" in df.columns and "torque" in df.columns:
            df["power"] = df["rotational_speed"] * df["torque"]
            df["power_normalized"] = df["power"] / (df["power"].max() + 1e-6)

        # Wear rate (Tool wear / RPM)
        if "tool_wear" in df.columns and "rotational_speed" in df.columns:
            df["wear_rate"] = df["tool_wear"] / (df["rotational_speed"] + 1e-6)

        # Thermal stress (normalized)
        if "process_temperature" in df.columns:
            df["thermal_stress"] = (
                (df["process_temperature"] - df["process_temperature"].min())
                / (df["process_temperature"].max() - df["process_temperature"].min() + 1e-6)
            )

        # Mechanical stress (normalized torque * speed)
        if "torque" in df.columns and "rotational_speed" in df.columns:
            mechanical_load = df["torque"] * df["rotational_speed"]
            df["mechanical_stress"] = (mechanical_load - mechanical_load.min()) / (
                mechanical_load.max() - mechanical_load.min() + 1e-6
            )

        # Vibration energy (scaled)
        if "vibration" in df.columns:
            df["vibration_energy"] = df["vibration"] ** 2

        return df

    @staticmethod
    def create_rolling_features(
        df: pd.DataFrame, windows: list = None, columns: list = None
    ) -> pd.DataFrame:
        """Create rolling statistics for time-series data."""
        if windows is None:
            windows = [5, 10, 20]
        if columns is None:
            columns = [
                "process_temperature",
                "rotational_speed",
                "torque",
                "tool_wear",
                "vibration",
            ]

        for col in columns:
            if col not in df.columns:
                continue
            for window in windows:
                df[f"{col}_rolling_mean_{window}"] = df[col].rolling(window=window).mean()
                df[f"{col}_rolling_std_{window}"] = df[col].rolling(window=window).std()

        # Fill NaN values from rolling windows
        df = df.fillna(method="bfill").fillna(method="ffill")

        return df

    @staticmethod
    def engineer_features(df: pd.DataFrame, create_rolling: bool = False) -> pd.DataFrame:
        """Main feature engineering pipeline."""
        print("Engineering features...")

        # Create temporal features
        df = FeatureEngineer.create_temporal_features(df)

        # Create sensor-based features
        df = FeatureEngineer.create_sensor_features(df)

        # Create rolling features (optional, helps with time-series)
        if create_rolling:
            df = FeatureEngineer.create_rolling_features(df)

        print(f"✓ Total features engineered: {df.shape[1]}")
        return df


class PredictiveMaintenanceModel:
    """Train and evaluate predictive maintenance models."""

    def __init__(self, model_type: str = "gradient_boosting"):
        """
        Initialize model.

        Args:
            model_type: 'random_forest', 'gradient_boosting', 'lstm', or 'keras'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = RobustScaler()
        self.feature_names = None
        self.training_history = {}

    def _create_random_forest(self, n_estimators: int = 100):
        """Create Random Forest classifier."""
        return RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )

    def _create_gradient_boosting(self, n_estimators: int = 100):
        """Create Gradient Boosting classifier."""
        return GradientBoostingClassifier(
            n_estimators=n_estimators,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
        )

    def _create_lstm(self, input_shape: tuple):
        """Create LSTM model for sequence prediction."""
        if not HAS_TENSORFLOW:
            raise ImportError("TensorFlow/Keras is required to create or run an LSTM model, but it is not installed.")
        model = keras.Sequential(
            [
                layers.LSTM(64, activation="relu", input_shape=input_shape, return_sequences=True),
                layers.Dropout(0.2),
                layers.LSTM(32, activation="relu", return_sequences=False),
                layers.Dropout(0.2),
                layers.Dense(16, activation="relu"),
                layers.Dropout(0.2),
                layers.Dense(1, activation="sigmoid"),
            ]
        )
        model.compile(
            optimizer="adam", loss="binary_crossentropy", metrics=["accuracy", keras.metrics.AUC()]
        )
        return model

    def _create_keras_model(self, input_dim: int):
        """Create a Keras feedforward neural network for tabular prediction."""
        if not HAS_TENSORFLOW:
            raise ImportError("TensorFlow/Keras is required to create a Keras model, but it is not installed.")
        model = keras.Sequential(
            [
                layers.Dense(64, activation="relu", input_dim=input_dim),
                layers.Dropout(0.2),
                layers.Dense(32, activation="relu"),
                layers.Dropout(0.2),
                layers.Dense(16, activation="relu"),
                layers.Dropout(0.2),
                layers.Dense(1, activation="sigmoid"),
            ]
        )
        model.compile(
            optimizer="adam",
            loss="binary_crossentropy",
            metrics=["accuracy"]
        )
        return model

    def prepare_data(
        self, df: pd.DataFrame, target_col: str = "failure", test_size: float = 0.2
    ):
        """
        Prepare data for model training.

        Args:
            df: DataFrame with features and target
            target_col: Name of target column
            test_size: Fraction for test set

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Explicitly map unit-named columns from the original dataset format
        mapping = {
            "Air temperature [K]": "air_temperature",
            "Process temperature [K]": "process_temperature",
            "Rotational speed [rpm]": "rotational_speed",
            "Torque [Nm]": "torque",
            "Tool wear [min]": "tool_wear",
            "Machine failure": "failure"
        }
        for orig, clean in mapping.items():
            if clean not in df.columns and orig in df.columns:
                df[clean] = df[orig]

        # Handle missing target column
        if target_col not in df.columns:
            print(f"Warning: {target_col} not found. Creating synthetic target...")
            # Use tool wear > 180 as failure indicator
            df[target_col] = (df["tool_wear"] > 180).astype(int)

        # Enforce using exactly the 5 telemetry features specified in the dataset contract
        feature_cols = [
            "air_temperature",
            "process_temperature",
            "rotational_speed",
            "torque",
            "tool_wear"
        ]

        self.feature_names = feature_cols
        print(f"Training features selected: {self.feature_names}")

        X = df[feature_cols].fillna(0)
        y = df[target_col].astype(int)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42, stratify=y
        )

        return X_train, X_test, y_train, y_test

    def train(self, X_train, y_train, X_test=None, y_test=None):
        """Train the model."""
        print(f"Training {self.model_type} model...")

        if self.model_type == "random_forest":
            self.model = self._create_random_forest()
            self.model.fit(X_train, y_train)

        elif self.model_type == "gradient_boosting":
            self.model = self._create_gradient_boosting()
            self.model.fit(X_train, y_train)

        elif self.model_type == "lstm":
            # Reshape for LSTM (samples, timesteps, features)
            X_train_lstm = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
            self.model = self._create_lstm(input_shape=(1, X_train.shape[1]))
            history = self.model.fit(
                X_train_lstm,
                y_train,
                epochs=20,
                batch_size=32,
                validation_split=0.2,
                verbose=0,
            )
            self.training_history = history.history

        elif self.model_type == "keras":
            self.model = self._create_keras_model(input_dim=X_train.shape[1])
            history = self.model.fit(
                X_train,
                y_train,
                epochs=20,
                batch_size=32,
                validation_split=0.2,
                verbose=0,
            )
            self.training_history = history.history

        print("✓ Model training completed")

    def evaluate(self, X_test, y_test) -> dict:
        """Evaluate model performance."""
        print("\nEvaluating model...")

        if self.model_type in ["lstm", "keras"]:
            if self.model_type == "lstm":
                X_test_lstm = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
                y_pred_proba = self.model.predict(X_test_lstm, verbose=0).flatten()
            else:
                y_pred_proba = self.model.predict(X_test, verbose=0).flatten()
        else:
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        y_pred = (y_pred_proba > 0.5).astype(int)

        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "auc": roc_auc_score(y_test, y_pred_proba),
        }

        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, zero_division=0))

        print("\nMetrics:")
        for metric, value in metrics.items():
            print(f"  {metric.upper()}: {value:.4f}")

        return metrics

    def predict(self, X):
        """Make predictions on new data."""
        if self.model is None:
            raise ValueError("Model not trained yet")

        if self.model_type in ["lstm", "keras"]:
            if self.model_type == "lstm":
                X_lstm = X.reshape((X.shape[0], 1, X.shape[1]))
                return self.model.predict(X_lstm, verbose=0).flatten()
            else:
                return self.model.predict(X, verbose=0).flatten()
        else:
            return self.model.predict_proba(X)[:, 1]

    def save_model(self, output_dir: str = "models"):
        """Save trained model and scaler."""
        Path(output_dir).mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = f"{self.model_type}_{timestamp}"

        if self.model_type in ["lstm", "keras"]:
            if not HAS_TENSORFLOW:
                raise ImportError(f"TensorFlow/Keras is required to save a {self.model_type} model, but it is not installed.")
            model_path = Path(output_dir) / f"{model_name}.h5"
            self.model.save(model_path)
        else:
            model_path = Path(output_dir) / f"{model_name}.pkl"
            with open(model_path, "wb") as f:
                pickle.dump(self.model, f)

        # Save scaler
        scaler_path = Path(output_dir) / f"{model_name}_scaler.pkl"
        with open(scaler_path, "wb") as f:
            pickle.dump(self.scaler, f)

        # Save feature names
        feature_path = Path(output_dir) / f"{model_name}_features.json"
        with open(feature_path, "w") as f:
            json.dump(self.feature_names, f)

        print(f"\n✓ Model saved: {model_path}")
        print(f"✓ Scaler saved: {scaler_path}")
        print(f"✓ Features saved: {feature_path}")

        return str(model_path)

    def load_model(self, model_path: str):
        """Load a trained model."""
        if self.model_type in ["lstm", "keras"]:
            if not HAS_TENSORFLOW:
                raise ImportError(f"TensorFlow/Keras is required to load a {self.model_type} model, but it is not installed.")
            self.model = keras.models.load_model(model_path)
        else:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)

        print(f"✓ Model loaded: {model_path}")


def main():
    """Demo: Complete ML pipeline."""
    print("=" * 80)
    print("Industrial AI Platform - ML Pipeline")
    print("=" * 80)

    # 1. Load dataset
    print("\n1. Loading dataset...")
    data_path = Path("data/engineered_ai4i.csv")
    if not data_path.exists():
        data_path = Path("data/ai4i2020_cleaned.csv")

    if not data_path.exists():
        print("Error: No dataset found. Run sensor_simulator.py first.")
        return

    df = pd.read_csv(data_path)
    print(f"   Loaded {len(df)} samples with {df.shape[1]} columns")

    # 2. Feature engineering
    print("\n2. Feature engineering...")
    engineer = FeatureEngineer()
    df = engineer.engineer_features(df, create_rolling=False)

    # 3. Train models
    models_to_train = ["gradient_boosting", "random_forest"]
    if HAS_TENSORFLOW:
        models_to_train.append("keras")

    for model_type in models_to_train:
        print(f"\n{'=' * 80}")
        print(f"Training {model_type.upper()} Model")
        print(f"{'=' * 80}")

        # Prepare data
        model = PredictiveMaintenanceModel(model_type=model_type)
        X_train, X_test, y_train, y_test = model.prepare_data(df)

        print(f"   Training set: {X_train.shape[0]} samples")
        print(f"   Test set: {X_test.shape[0]} samples")
        print(f"   Features: {X_train.shape[1]}")

        # Train
        model.train(X_train, y_train)

        # Evaluate
        metrics = model.evaluate(X_test, y_test)

        # Save
        saved_path = model.save_model("models")

        # Copy keras model as best_model.h5 for deployment
        if model_type == "keras":
            import shutil
            shutil.copy(saved_path, Path("models") / "best_model.h5")
            # Copy its scaler
            timestamp = saved_path.split("_")[-2] + "_" + saved_path.split("_")[-1].replace(".h5", "")
            shutil.copy(Path("models") / f"keras_{timestamp}_scaler.pkl", Path("models") / "scaler.pkl")
            print("✓ Copied Keras model to models/best_model.h5 and its scaler to models/scaler.pkl")
        elif model_type == "gradient_boosting":
            import shutil
            shutil.copy(saved_path, Path("models") / "best_model.pkl")
            # Copy its scaler
            timestamp = saved_path.split("_")[-2] + "_" + saved_path.split("_")[-1].replace(".pkl", "")
            shutil.copy(Path("models") / f"gradient_boosting_{timestamp}_scaler.pkl", Path("models") / "scaler.pkl")
            print("✓ Copied Gradient Boosting model to models/best_model.pkl and its scaler to models/scaler.pkl")

    print("\n" + "=" * 80)
    print("ML Pipeline completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
