import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("base_dir:", base_dir)
sys.path.insert(0, base_dir)
print("sys.path:", sys.path)

try:
    import backend
    print("SUCCESS importing backend")
    print("backend file:", backend.__file__)
    print("backend path:", getattr(backend, "__path__", None))
    
    import backend.database
    print("SUCCESS importing backend.database")
    
    from backend.database.connection import SessionLocal
    print("SUCCESS importing SessionLocal:", SessionLocal)
except Exception as e:
    print("FAILED import:", e)
    import traceback
    traceback.print_exc()
