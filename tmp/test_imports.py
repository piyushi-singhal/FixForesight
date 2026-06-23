import sys
import os

print("1. Standard imports...")
import sys
import os
print("OK")

print("2. Setting environment...")
workspace_dir = "/Users/piyushisinghal/Downloads/FixForesight"
cache_dir = os.path.join(workspace_dir, "tmp", "cache")
os.makedirs(cache_dir, exist_ok=True)
os.environ["DATABASE_URL"] = "sqlite:///pdm_db.db"
os.environ["XDG_CACHE_HOME"] = cache_dir
os.environ["JOBLIB_TEMP_FOLDER"] = cache_dir
os.environ["MPLCONFIGDIR"] = cache_dir
os.environ["PYTHON_EGG_CACHE"] = cache_dir

sys.path.insert(0, "/Users/piyushisinghal/Downloads/FixForesight/venv/lib/python3.14/site-packages")
sys.path.insert(0, workspace_dir)
print("OK")

print("3. Importing sqlalchemy...")
import sqlalchemy
print("OK")

print("4. Importing database models...")
from backend.database.connection import SessionLocal
from backend.database.models import Machine
print("OK")

print("5. Importing joblib and numpy...")
import joblib
import numpy as np
print("OK")

print("6. Loading best_model.pkl directly...")
pkl_model_path = os.path.join(workspace_dir, "models", "best_model.pkl")
scaler_path = os.path.join(workspace_dir, "models", "scaler.pkl")
if os.path.exists(pkl_model_path):
    print("Found best_model.pkl, loading...")
    model = joblib.load(pkl_model_path)
    print("Model loaded successfully")
if os.path.exists(scaler_path):
    print("Found scaler.pkl, loading...")
    scaler = joblib.load(scaler_path)
    print("Scaler loaded successfully")
print("OK")

print("7. Importing db_service...")
from backend.services import db_service
print("OK")
