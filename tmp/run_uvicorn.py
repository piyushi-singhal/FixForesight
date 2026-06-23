import os
import sys

workspace_dir = "/Users/piyushisinghal/Downloads/FixForesight"
sys.path.insert(0, workspace_dir)
os.environ["PYTHONPATH"] = workspace_dir

import uvicorn

if __name__ == "__main__":
    print("Starting uvicorn on port 8001...")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8001)
