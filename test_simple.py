import sys
sys.path.insert(0, "/Users/piyushisinghal/Downloads/FixForesight/venv/lib/python3.14/site-packages")
sys.path.insert(0, "/Users/piyushisinghal/Downloads/FixForesight")
import os
os.environ["DATABASE_URL"] = "sqlite:///pdm_db.db"

print("Before importing backend.database.connection")
from backend.database.connection import SessionLocal
print("SessionLocal imported successfully")
