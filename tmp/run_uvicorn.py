import os
import sys

from pathlib import Path

# Resolve PROJECT_ROOT based on file location (tmp/run_uvicorn.py -> Project Root)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["PYTHONPATH"] = str(PROJECT_ROOT)

import uvicorn

if __name__ == "__main__":
    print("Starting uvicorn on port 8000...")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000)
