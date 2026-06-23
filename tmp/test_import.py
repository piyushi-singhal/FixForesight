import sys
import os

# Set cache directories to workspace-local paths to prevent sandbox violations
workspace_dir = "/Users/piyushisinghal/Downloads/FixForesight"
cache_dir = os.path.join(workspace_dir, "tmp", "cache")
os.makedirs(cache_dir, exist_ok=True)

os.environ["DATABASE_URL"] = "sqlite:///pdm_db.db"
os.environ["XDG_CACHE_HOME"] = cache_dir
os.environ["JOBLIB_TEMP_FOLDER"] = cache_dir
os.environ["MPLCONFIGDIR"] = cache_dir
os.environ["PYTHON_EGG_CACHE"] = cache_dir

# Add workspace directory and virtual environment packages to path
sys.path.insert(0, "/Users/piyushisinghal/Downloads/FixForesight/venv/lib/python3.14/site-packages")
sys.path.insert(0, "/Users/piyushisinghal/Downloads/FixForesight")

from backend.services import db_service

print("=== Testing db_service.search_incidents fallback ===")

# Test 1: search_incidents('*')
res1 = db_service.search_incidents('*')
print(f"Query '*': numFound = {res1.get('numFound')}, docs count = {len(res1.get('docs', []))}")

# Test 2: search_incidents('M101')
res2 = db_service.search_incidents('M101')
print(f"Query 'M101': numFound = {res2.get('numFound')}, docs count = {len(res2.get('docs', []))}")

# Test 3: search_incidents('Mitigation')
res3 = db_service.search_incidents('Mitigation')
print(f"Query 'Mitigation': numFound = {res3.get('numFound')}, docs count = {len(res3.get('docs', []))}")
