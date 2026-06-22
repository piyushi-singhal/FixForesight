"""
Industrial AI Platform - Sensor Data Simulator
Generates realistic machine telemetry data with various failure scenarios
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random
import json
from pathlib import Path


class SensorSimulator:
    """Simulate realistic machine sensor data with failure scenarios."""

    def __init__(self, seed: int = 42):
        """
        Initialize the simulator.

        Args:
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        random.seed(seed)

        # Define sensor specifications
        self.sensor_specs = {
            "air_temperature": {"min": 293.15, "max": 313.15, "unit": "K"},
            "process_temperature": {"min": 308.15, "max": 333.15, "unit": "K"},
            "rotational_speed": {"min": 1000, "max": 3000, "unit": "rpm"},
            "torque": {"min": 3, "max": 100, "unit": "Nm"},
            "tool_wear": {"min": 0, "max": 240, "unit": "min"},
            "vibration": {"min": 0, "max": 50, "unit": "mm/s"},
        }

        self.failure_modes = [
            "heat_dissipation",
            "power_loss",
            "overstrain",
            "tool_wear",
            "random_failure",
        ]

    def generate_normal_operation(
        self, num_samples: int = 1000, start_time: datetime = None
    ) -> pd.DataFrame:
        """
        Generate sensor data for normal machine operation.

        Args:
            num_samples: Number of samples to generate
            start_time: Start timestamp (default: now)

        Returns:
            DataFrame with simulated sensor readings
        """
        if start_time is None:
            start_time = datetime.now() - timedelta(hours=num_samples)

        timestamps = [start_time + timedelta(seconds=i * 60) for i in range(num_samples)]

        data = {
            "timestamp": timestamps,
            "air_temperature": np.random.normal(303, 5, num_samples),
            "process_temperature": np.random.normal(320, 8, num_samples),
            "rotational_speed": np.random.normal(2000, 200, num_samples),
            "torque": np.random.normal(50, 15, num_samples),
            "tool_wear": np.linspace(0, 100, num_samples) + np.random.normal(0, 5, num_samples),
            "vibration": np.random.normal(10, 3, num_samples),
        }

        df = pd.DataFrame(data)

        # Clip values to valid ranges
        for col, spec in self.sensor_specs.items():
            if col in df.columns:
                df[col] = df[col].clip(spec["min"], spec["max"])

        return df

    def generate_failure_scenario(
        self,
        failure_type: str = None,
        num_samples_normal: int = 500,
        num_samples_degradation: int = 200,
        start_time: datetime = None,
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Generate sensor data with progressive degradation leading to failure.

        Args:
            failure_type: Type of failure ('heat_dissipation', 'power_loss', 'overstrain', 'tool_wear')
            num_samples_normal: Samples before degradation
            num_samples_degradation: Samples during degradation phase
            start_time: Start timestamp

        Returns:
            Tuple of (DataFrame, metadata dict with failure info)
        """
        if start_time is None:
            start_time = datetime.now() - timedelta(
                hours=(num_samples_normal + num_samples_degradation)
            )

        if failure_type is None:
            failure_type = random.choice(self.failure_modes)

        # Normal operation phase
        timestamps = [start_time + timedelta(seconds=i * 60) for i in range(num_samples_normal)]
        normal_data = {
            "timestamp": timestamps,
            "air_temperature": np.random.normal(303, 5, num_samples_normal),
            "process_temperature": np.random.normal(320, 8, num_samples_normal),
            "rotational_speed": np.random.normal(2000, 200, num_samples_normal),
            "torque": np.random.normal(50, 15, num_samples_normal),
            "tool_wear": np.linspace(0, 80, num_samples_normal) + np.random.normal(0, 3, num_samples_normal),
            "vibration": np.random.normal(10, 3, num_samples_normal),
        }

        # Degradation phase - anomalies based on failure type
        degradation_start = start_time + timedelta(seconds=num_samples_normal * 60)
        timestamps_deg = [
            degradation_start + timedelta(seconds=i * 60) for i in range(num_samples_degradation)
        ]

        # Degradation progression (0 to 1, where 1 is failure)
        degradation_factor = np.linspace(0, 1, num_samples_degradation)

        if failure_type == "heat_dissipation":
            # Temperature increases progressively
            process_temp = np.random.normal(320, 8, num_samples_degradation)
            process_temp += degradation_factor * 30  # Up to 30K increase
            degradation_data = {
                "timestamp": timestamps_deg,
                "air_temperature": np.random.normal(303, 5, num_samples_degradation),
                "process_temperature": process_temp,
                "rotational_speed": np.random.normal(2000, 200, num_samples_degradation),
                "torque": np.random.normal(50, 15, num_samples_degradation),
                "tool_wear": np.linspace(80, 150, num_samples_degradation),
                "vibration": np.random.normal(10, 3, num_samples_degradation) + degradation_factor * 20,
            }

        elif failure_type == "power_loss":
            # Torque decreases, speed varies
            degradation_data = {
                "timestamp": timestamps_deg,
                "air_temperature": np.random.normal(303, 5, num_samples_degradation),
                "process_temperature": np.random.normal(320, 8, num_samples_degradation),
                "rotational_speed": np.random.normal(2000, 200, num_samples_degradation) - degradation_factor * 600,
                "torque": np.random.normal(50, 15, num_samples_degradation) - degradation_factor * 40,
                "tool_wear": np.linspace(80, 150, num_samples_degradation),
                "vibration": np.random.normal(10, 3, num_samples_degradation) + degradation_factor * 15,
            }

        elif failure_type == "overstrain":
            # Torque and vibration increase
            degradation_data = {
                "timestamp": timestamps_deg,
                "air_temperature": np.random.normal(303, 5, num_samples_degradation) + degradation_factor * 15,
                "process_temperature": np.random.normal(320, 8, num_samples_degradation) + degradation_factor * 20,
                "rotational_speed": np.random.normal(2000, 200, num_samples_degradation),
                "torque": np.random.normal(50, 15, num_samples_degradation) + degradation_factor * 50,
                "tool_wear": np.linspace(80, 150, num_samples_degradation),
                "vibration": np.random.normal(10, 3, num_samples_degradation) + degradation_factor * 30,
            }

        elif failure_type == "tool_wear":
            # Tool wear increases rapidly
            degradation_data = {
                "timestamp": timestamps_deg,
                "air_temperature": np.random.normal(303, 5, num_samples_degradation),
                "process_temperature": np.random.normal(320, 8, num_samples_degradation) + degradation_factor * 10,
                "rotational_speed": np.random.normal(2000, 200, num_samples_degradation) - degradation_factor * 200,
                "torque": np.random.normal(50, 15, num_samples_degradation) + degradation_factor * 30,
                "tool_wear": np.linspace(80, 240, num_samples_degradation),
                "vibration": np.random.normal(10, 3, num_samples_degradation) + degradation_factor * 20,
            }

        else:  # random_failure
            # Random spikes in multiple sensors
            degradation_data = {
                "timestamp": timestamps_deg,
                "air_temperature": np.random.normal(303, 5, num_samples_degradation) + degradation_factor * np.random.normal(0, 20, num_samples_degradation),
                "process_temperature": np.random.normal(320, 8, num_samples_degradation) + degradation_factor * np.random.normal(0, 25, num_samples_degradation),
                "rotational_speed": np.random.normal(2000, 200, num_samples_degradation) + degradation_factor * np.random.normal(0, 300, num_samples_degradation),
                "torque": np.random.normal(50, 15, num_samples_degradation) + degradation_factor * np.random.normal(0, 40, num_samples_degradation),
                "tool_wear": np.linspace(80, 200, num_samples_degradation),
                "vibration": np.random.normal(10, 3, num_samples_degradation) + degradation_factor * np.random.normal(0, 35, num_samples_degradation),
            }

        # Combine normal and degradation phases
        all_data = {}
        for key in normal_data.keys():
            if isinstance(normal_data[key], list):
                all_data[key] = normal_data[key] + degradation_data[key]
            else:
                all_data[key] = np.concatenate([normal_data[key], degradation_data[key]])

        df = pd.DataFrame(all_data)

        # Clip values to valid ranges
        for col, spec in self.sensor_specs.items():
            if col in df.columns:
                df[col] = df[col].clip(spec["min"], spec["max"])

        # Metadata about the failure scenario
        metadata = {
            "failure_type": failure_type,
            "failure_time": timestamps_deg[-1],
            "degradation_start": degradation_start,
            "num_normal_samples": num_samples_normal,
            "num_degradation_samples": num_samples_degradation,
        }

        return df, metadata

    def generate_multiple_machines_dataset(
        self, num_machines: int = 5, samples_per_machine: int = 1000
    ) -> pd.DataFrame:
        """
        Generate dataset for multiple machines with mixed scenarios.

        Args:
            num_machines: Number of machines to simulate
            samples_per_machine: Samples per machine

        Returns:
            DataFrame with machine_id and sensor data
        """
        all_data = []

        for machine_id in range(1, num_machines + 1):
            # 70% normal operation, 30% degradation scenarios
            if random.random() < 0.7:
                df = self.generate_normal_operation(num_samples=samples_per_machine)
                status = "normal"
            else:
                df, _ = self.generate_failure_scenario(num_samples_normal=int(0.7 * samples_per_machine))
                status = "degrading"

            df["machine_id"] = machine_id
            df["status"] = status

            all_data.append(df)

        combined_df = pd.concat(all_data, ignore_index=True)
        return combined_df.sort_values("timestamp").reset_index(drop=True)

    def generate_batch_dataset_from_ai4i(
        self, ai4i_csv_path: str, output_path: str = None
    ) -> pd.DataFrame:
        """
        Generate augmented dataset from AI4I 2020 data by adding synthetic degradation patterns.

        Args:
            ai4i_csv_path: Path to AI4I 2020 CSV file
            output_path: Path to save augmented dataset (optional)

        Returns:
            Augmented DataFrame
        """
        df = pd.read_csv(ai4i_csv_path)

        # Rename columns for consistency
        df = df.rename(
            columns={
                "Air temperature [K]": "air_temperature",
                "Process temperature [K]": "process_temperature",
                "Rotational speed [rpm]": "rotational_speed",
                "Torque [Nm]": "torque",
                "Tool wear [min]": "tool_wear",
            }
        )

        # Add synthetic features from simulator
        df["vibration"] = np.random.normal(10, 3, len(df)).clip(0, 50)

        # Add machine_id if not present
        if "machine_id" not in df.columns:
            df["machine_id"] = (df.index % 10) + 1

        # Add degradation flags based on sensor anomalies
        df["is_anomalous"] = False
        temp_anomaly = (df["process_temperature"] > df["process_temperature"].quantile(0.95))
        vibration_anomaly = (df["vibration"] > df["vibration"].quantile(0.95))
        wear_anomaly = (df["tool_wear"] > df["tool_wear"].quantile(0.95))

        df.loc[temp_anomaly | vibration_anomaly | wear_anomaly, "is_anomalous"] = True

        if output_path:
            df.to_csv(output_path, index=False)
            print(f"Augmented dataset saved to {output_path}")

        return df


def main():
    """Demo: Generate and save simulated data."""
    print("=" * 80)
    print("Industrial AI Platform - Sensor Data Simulator")
    print("=" * 80)

    simulator = SensorSimulator()

    # 1. Generate normal operation data
    print("\n1. Generating normal operation data...")
    normal_df = simulator.generate_normal_operation(num_samples=1000)
    normal_df.to_csv("data/simulated_normal_operation.csv", index=False)
    print(f"   Generated {len(normal_df)} samples of normal operation")
    print(f"   Saved to: data/simulated_normal_operation.csv")

    # 2. Generate failure scenarios
    print("\n2. Generating failure scenarios...")
    for failure_type in ["heat_dissipation", "power_loss", "overstrain", "tool_wear"]:
        df, metadata = simulator.generate_failure_scenario(
            failure_type=failure_type, num_samples_normal=300, num_samples_degradation=150
        )
        output_file = f"data/simulated_{failure_type}.csv"
        df.to_csv(output_file, index=False)
        print(f"   {failure_type}: {len(df)} samples → {output_file}")
        print(f"      Failure time: {metadata['failure_time']}")

    # 3. Generate multi-machine dataset
    print("\n3. Generating multi-machine dataset...")
    multi_machine_df = simulator.generate_multiple_machines_dataset(
        num_machines=5, samples_per_machine=500
    )
    multi_machine_df.to_csv("data/simulated_multi_machine.csv", index=False)
    print(f"   Generated {len(multi_machine_df)} samples for 5 machines")
    print(f"   Saved to: data/simulated_multi_machine.csv")

    # 4. Print summary statistics
    print("\n" + "=" * 80)
    print("Summary Statistics (Normal Operation)")
    print("=" * 80)
    print(normal_df.describe())

    print("\n" + "=" * 80)
    print("Files generated:")
    print("=" * 80)
    print("  • data/simulated_normal_operation.csv")
    print("  • data/simulated_heat_dissipation.csv")
    print("  • data/simulated_power_loss.csv")
    print("  • data/simulated_overstrain.csv")
    print("  • data/simulated_tool_wear.csv")
    print("  • data/simulated_multi_machine.csv")


if __name__ == "__main__":
    main()
