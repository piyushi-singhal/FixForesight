"""
Industrial AI Platform - Data Ingestion Pipeline
Handles SQS → Spark → PostgreSQL data flow for real-time sensor data
"""

import json
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from typing import Dict, List, Optional
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PostgreSQLConnector:
    """Handle PostgreSQL database operations."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "predictive_maintenance",
        user: str = "postgres",
        password: str = "postgres",
    ):
        """
        Initialize database connection.

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
        }
        self.conn = None

    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            logger.info("Connected to PostgreSQL database")
            return self.conn
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from PostgreSQL")

    def insert_sensor_readings(self, readings: List[Dict]) -> int:
        """
        Insert sensor readings into database.

        Args:
            readings: List of sensor reading dicts with keys:
                - sensor_id
                - machine_id
                - value
                - timestamp

        Returns:
            Number of rows inserted
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        try:
            query = """
                INSERT INTO sensor_readings (sensor_id, machine_id, value, timestamp)
                VALUES %s
                ON CONFLICT DO NOTHING
            """

            values = [
                (
                    reading["sensor_id"],
                    reading["machine_id"],
                    reading["value"],
                    reading["timestamp"],
                )
                for reading in readings
            ]

            execute_values(cursor, query, values, page_size=1000)
            self.conn.commit()

            rows_inserted = cursor.rowcount
            logger.info(f"Inserted {rows_inserted} sensor readings")

            return rows_inserted

        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"Error inserting sensor readings: {e}")
            raise
        finally:
            cursor.close()

    def insert_predictions(self, predictions: List[Dict]) -> int:
        """
        Insert ML predictions into database.

        Args:
            predictions: List of prediction dicts with keys:
                - machine_id
                - prediction_timestamp
                - failure_probability
                - risk_level
                - failure_type
                - days_to_failure
                - confidence_score
                - model_version

        Returns:
            Number of rows inserted
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        try:
            query = """
                INSERT INTO predictions
                (machine_id, prediction_timestamp, failure_probability, risk_level,
                 failure_type, days_to_failure, confidence_score, model_version)
                VALUES %s
            """

            values = [
                (
                    pred["machine_id"],
                    pred["prediction_timestamp"],
                    pred["failure_probability"],
                    pred.get("risk_level", "unknown"),
                    pred.get("failure_type", "unknown"),
                    pred.get("days_to_failure"),
                    pred.get("confidence_score", 0.0),
                    pred.get("model_version", "1.0"),
                )
                for pred in predictions
            ]

            execute_values(cursor, query, values, page_size=500)
            self.conn.commit()

            rows_inserted = cursor.rowcount
            logger.info(f"Inserted {rows_inserted} predictions")

            return rows_inserted

        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"Error inserting predictions: {e}")
            raise
        finally:
            cursor.close()

    def insert_recommendations(self, recommendations: List[Dict]) -> int:
        """
        Insert maintenance recommendations into database.

        Args:
            recommendations: List of recommendation dicts

        Returns:
            Number of rows inserted
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        try:
            query = """
                INSERT INTO recommendations
                (machine_id, prediction_id, recommendation_type, action,
                 priority, estimated_cost, spare_parts, created_by)
                VALUES %s
            """

            values = [
                (
                    rec["machine_id"],
                    rec.get("prediction_id"),
                    rec["recommendation_type"],
                    rec["action"],
                    rec["priority"],
                    rec.get("estimated_cost", 0.0),
                    json.dumps(rec.get("spare_parts", [])),
                    "system",
                )
                for rec in recommendations
            ]

            execute_values(cursor, query, values, page_size=500)
            self.conn.commit()

            rows_inserted = cursor.rowcount
            logger.info(f"Inserted {rows_inserted} recommendations")

            return rows_inserted

        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"Error inserting recommendations: {e}")
            raise
        finally:
            cursor.close()

    def query_machines(self) -> pd.DataFrame:
        """Query all machines from database."""
        if not self.conn:
            self.connect()

        try:
            query = "SELECT machine_id, name, status FROM machines"
            df = pd.read_sql(query, self.conn)
            return df
        except psycopg2.Error as e:
            logger.error(f"Error querying machines: {e}")
            raise

    def query_latest_predictions(self, machine_id: int = None) -> pd.DataFrame:
        """Query latest predictions."""
        if not self.conn:
            self.connect()

        try:
            if machine_id:
                query = """
                    SELECT DISTINCT ON (machine_id)
                        machine_id, failure_probability, risk_level,
                        days_to_failure, prediction_timestamp
                    FROM predictions
                    WHERE machine_id = %s
                    ORDER BY machine_id, prediction_timestamp DESC
                """
                df = pd.read_sql(query, self.conn, params=(machine_id,))
            else:
                query = """
                    SELECT DISTINCT ON (machine_id)
                        machine_id, failure_probability, risk_level,
                        days_to_failure, prediction_timestamp
                    FROM predictions
                    ORDER BY machine_id, prediction_timestamp DESC
                """
                df = pd.read_sql(query, self.conn)

            return df
        except psycopg2.Error as e:
            logger.error(f"Error querying predictions: {e}")
            raise


class SensorDataProcessor:
    """Process raw sensor data for ingestion."""

    @staticmethod
    def parse_sensor_message(message: Dict) -> Dict:
        """
        Parse raw sensor message from SQS.

        Expected format:
        {
            "machine_id": 1,
            "sensor_id": 1,
            "sensor_type": "temperature",
            "value": 320.5,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        """
        try:
            return {
                "machine_id": int(message["machine_id"]),
                "sensor_id": int(message["sensor_id"]),
                "value": float(message["value"]),
                "timestamp": message["timestamp"],
            }
        except (KeyError, ValueError) as e:
            logger.warning(f"Failed to parse sensor message: {e}")
            return None

    @staticmethod
    def batch_process_readings(messages: List[Dict]) -> List[Dict]:
        """
        Process batch of sensor messages.

        Args:
            messages: List of raw sensor messages

        Returns:
            List of parsed readings
        """
        readings = []
        for msg in messages:
            reading = SensorDataProcessor.parse_sensor_message(msg)
            if reading:
                readings.append(reading)

        logger.info(f"Processed {len(readings)} out of {len(messages)} messages")
        return readings

    @staticmethod
    def validate_readings(readings: List[Dict], sensor_specs: Dict) -> List[Dict]:
        """
        Validate sensor readings against specifications.

        Args:
            readings: List of readings
            sensor_specs: Dict mapping sensor_id to min/max values

        Returns:
            List of validated readings
        """
        valid_readings = []

        for reading in readings:
            sensor_id = reading["sensor_id"]
            value = reading["value"]

            # Check if sensor spec exists
            if sensor_id not in sensor_specs:
                logger.warning(f"Unknown sensor: {sensor_id}")
                continue

            spec = sensor_specs[sensor_id]

            # Check if value is within range
            if spec["min"] <= value <= spec["max"]:
                valid_readings.append(reading)
            else:
                logger.warning(
                    f"Sensor {sensor_id} value {value} out of range [{spec['min']}, {spec['max']}]"
                )

        return valid_readings


class DataIngestionPipeline:
    """Main data ingestion pipeline."""

    def __init__(
        self,
        db_host: str = "localhost",
        db_port: int = 5432,
        db_name: str = "predictive_maintenance",
        db_user: str = "postgres",
        db_password: str = "postgres",
    ):
        """
        Initialize pipeline.

        Args:
            db_host: PostgreSQL host
            db_port: PostgreSQL port
            db_name: Database name
            db_user: Database user
            db_password: Database password
        """
        self.db = PostgreSQLConnector(
            host=db_host, port=db_port, database=db_name, user=db_user, password=db_password
        )

        # Sensor specifications
        self.sensor_specs = {
            1: {"min": 293.15, "max": 323.15, "name": "air_temperature"},
            2: {"min": 308.15, "max": 333.15, "name": "process_temperature"},
            3: {"min": 1000, "max": 3000, "name": "rotational_speed"},
            4: {"min": 3, "max": 100, "name": "torque"},
            5: {"min": 0, "max": 240, "name": "tool_wear"},
            6: {"min": 0, "max": 50, "name": "vibration"},
        }

    def ingest_sensor_data(self, csv_path: str, batch_size: int = 1000) -> int:
        """
        Ingest sensor data from CSV file.

        Args:
            csv_path: Path to CSV file
            batch_size: Number of rows to process at once

        Returns:
            Total rows ingested
        """
        logger.info(f"Starting data ingestion from {csv_path}")

        try:
            self.db.connect()

            # Read CSV in chunks
            total_inserted = 0
            chunk_size = batch_size

            for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
                # Convert DataFrame to list of dicts
                messages = chunk.to_dict("records")

                # Process messages
                readings = SensorDataProcessor.batch_process_readings(messages)

                # Validate readings
                readings = SensorDataProcessor.validate_readings(readings, self.sensor_specs)

                # Insert into database
                if readings:
                    inserted = self.db.insert_sensor_readings(readings)
                    total_inserted += inserted

            logger.info(f"Total rows ingested: {total_inserted}")
            return total_inserted

        except Exception as e:
            logger.error(f"Error during ingestion: {e}")
            raise
        finally:
            self.db.disconnect()

    def process_predictions(self, predictions: List[Dict]) -> int:
        """
        Process and store ML predictions.

        Args:
            predictions: List of prediction dicts

        Returns:
            Number of predictions inserted
        """
        try:
            self.db.connect()
            inserted = self.db.insert_predictions(predictions)
            return inserted
        except Exception as e:
            logger.error(f"Error processing predictions: {e}")
            raise
        finally:
            self.db.disconnect()

    def store_recommendations(self, recommendations: List[Dict]) -> int:
        """
        Store maintenance recommendations.

        Args:
            recommendations: List of recommendation dicts

        Returns:
            Number of recommendations inserted
        """
        try:
            self.db.connect()
            inserted = self.db.insert_recommendations(recommendations)
            return inserted
        except Exception as e:
            logger.error(f"Error storing recommendations: {e}")
            raise
        finally:
            self.db.disconnect()


def main():
    """Demo: Run data ingestion pipeline."""
    print("=" * 80)
    print("Industrial AI Platform - Data Ingestion Pipeline")
    print("=" * 80)

    # Initialize pipeline
    pipeline = DataIngestionPipeline()

    # Check if data file exists
    data_file = Path("data/simulated_multi_machine.csv")
    if not data_file.exists():
        print("\nNote: To test ingestion, run sensor_simulator.py first to generate data")
        print("Example usage:")
        print("  python sensor_simulator.py")
        print("  python data_pipeline.py")
        return

    # Ingest sensor data
    print("\n1. Ingesting sensor data...")
    try:
        total_rows = pipeline.ingest_sensor_data("data/simulated_multi_machine.csv", batch_size=500)
        print(f"✓ Successfully ingested {total_rows} sensor readings")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Example: Store sample predictions
    print("\n2. Storing sample predictions...")
    sample_predictions = [
        {
            "machine_id": 1,
            "prediction_timestamp": datetime.now().isoformat(),
            "failure_probability": 0.75,
            "risk_level": "high",
            "failure_type": "heat_dissipation",
            "days_to_failure": 3,
            "confidence_score": 0.92,
            "model_version": "1.0",
        },
        {
            "machine_id": 2,
            "prediction_timestamp": datetime.now().isoformat(),
            "failure_probability": 0.45,
            "risk_level": "medium",
            "failure_type": "tool_wear",
            "days_to_failure": 7,
            "confidence_score": 0.85,
            "model_version": "1.0",
        },
    ]

    try:
        inserted = pipeline.process_predictions(sample_predictions)
        print(f"✓ Stored {inserted} predictions")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Example: Store sample recommendations
    print("\n3. Storing sample recommendations...")
    sample_recommendations = [
        {
            "machine_id": 1,
            "prediction_id": 1,
            "recommendation_type": "urgent",
            "action": "Replace cooling fan within 24 hours",
            "priority": "high",
            "estimated_cost": 500.0,
            "spare_parts": [{"part_name": "Cooling Fan Assembly", "quantity": 1}],
        },
    ]

    try:
        inserted = pipeline.store_recommendations(sample_recommendations)
        print(f"✓ Stored {inserted} recommendations")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 80)
    print("Pipeline demonstration completed")
    print("=" * 80)


if __name__ == "__main__":
    main()
