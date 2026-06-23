"""
FixForesight — Dataset -> Model -> Predictions & Recommendations Pipeline
Implements STEP 7 (Store Predictions) and STEP 8 (Rule-based Recommendations)
"""

import os
import sys

# Set cache directories and add venv site-packages to python system path
workspace_dir = "/Users/piyushisinghal/Downloads/FixForesight"
cache_dir = os.path.join(workspace_dir, "tmp", "cache")
os.makedirs(cache_dir, exist_ok=True)
os.environ["XDG_CACHE_HOME"] = cache_dir
os.environ["JOBLIB_TEMP_FOLDER"] = cache_dir
os.environ["MPLCONFIGDIR"] = cache_dir
os.environ["PYTHON_EGG_CACHE"] = cache_dir

sys.path.insert(0, "/Users/piyushisinghal/Downloads/FixForesight/venv/lib/python3.14/site-packages")
sys.path.insert(0, workspace_dir)
sys.path.insert(0, os.path.join(workspace_dir, "src"))

import pandas as pd
from pathlib import Path

from src.backend_copy.database.connection import SessionLocal
from src.backend_copy.database.models import Machine, Prediction, Recommendation
from src.backend_copy.services.db_service import predict_machine_failure

def run_predictions_pipeline(limit=100):
    print("=" * 80)
    print("FixForesight Ingestion and Prediction Pipeline")
    print("=" * 80)

    # 1. Locate dataset
    data_path = Path(workspace_dir) / "data" / "engineered_ai4i.csv"
    if not data_path.exists():
        data_path = Path(workspace_dir) / "data" / "ai4i2020_cleaned.csv"
        
    if not data_path.exists():
        print(f"Error: Telemetry dataset not found at {data_path}")
        return
        
    print(f"Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    
    # Standardize column names to snake_case
    df = df.rename(columns={
        "Air temperature [K]": "air_temperature",
        "Process temperature [K]": "process_temperature",
        "Rotational speed [rpm]": "rotational_speed",
        "Torque [Nm]": "torque",
        "Tool wear [min]": "tool_wear",
        "Machine failure": "failure"
    })
    
    db_sess = SessionLocal()
    try:
        # Clear existing records to ensure a fresh import
        print("Clearing existing tables in database...")
        db_sess.query(Recommendation).delete()
        db_sess.query(Prediction).delete()
        db_sess.query(Machine).delete()
        db_sess.commit()
        print("✓ Database cleared.")

        print(f"Processing first {limit} rows from dataset...")
        count = 0
        for idx, row in df.head(limit).iterrows():
            # Generate a clean machine ID based on UDI
            udi = int(row.get("UDI", idx + 1))
            machine_id = f"M{100 + udi}"
            
            # Telemetry parameters
            air_temp = float(row["air_temperature"])
            proc_temp = float(row["process_temperature"])
            speed = int(row["rotational_speed"])
            torque = float(row["torque"])
            wear = float(row["tool_wear"])
            
            # Predict failure using the ML model
            prob, pred_fail, failure_type, time_to_fail = predict_machine_failure(
                air_temp, proc_temp, speed, torque, wear
            )
            
            # Machine status mapping
            status = "Healthy"
            if prob > 0.8:
                status = "Critical"
            elif prob > 0.4:
                status = "Warning"
                
            # Create machine record
            m = Machine(
                machine_id=machine_id,
                machine_name=f"Machine {row.get('Product ID', machine_id)}",
                status=status,
                air_temperature=air_temp,
                process_temperature=proc_temp,
                rotational_speed=speed,
                torque=torque,
                tool_wear=wear
            )
            db_sess.add(m)
            db_sess.flush() # Flush to resolve database key constraints
            
            # Store prediction (probability stored as percentage in [0, 100])
            pred = Prediction(
                machine_id=machine_id,
                failure_probability=prob * 100.0,
                predicted_failure=pred_fail,
                time_to_failure=time_to_fail
            )
            db_sess.add(pred)
            db_sess.flush()
            
            # Store recommendation (STEP 8: Rule-based recommendation engine)
            recommendation_text = "No active recommendations. Machine operation normal."
            priority = "Low"
            confidence = prob * 100.0
            
            # Apply rule-based thresholds (STEP 8)
            if prob > 0.8:
                recommendation_text = "Immediate Maintenance Required"
                priority = "Critical"
            elif prob > 0.5:
                recommendation_text = "Schedule preventive maintenance"
                priority = "Medium"
                
            rec = Recommendation(
                machine_id=machine_id,
                prediction_id=pred.prediction_id,
                recommendation=recommendation_text,
                priority=priority,
                confidence=confidence
            )
            db_sess.add(rec)
            
            count += 1
            
        db_sess.commit()
        print(f"✓ Pipeline run completed. Successfully processed and stored predictions/recommendations for {count} machines.")
        
    except Exception as e:
        db_sess.rollback()
        print(f"✗ Error executing pipeline: {e}")
        raise
    finally:
        db_sess.close()

if __name__ == "__main__":
    run_predictions_pipeline(limit=100)
