import sys
import os
sys.path.insert(0, "/Users/piyushisinghal/Downloads/FixForesight")
import backend
print("backend path:", backend.__path__)
try:
    print("backend directory contents:", os.listdir(backend.__path__[0]))
except Exception as e:
    print("Failed to list backend dir:", e)
