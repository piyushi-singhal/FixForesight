import os
print("Is backend/services a dir?", os.path.isdir("backend/services"))
try:
    print("Contents of backend/services:", os.listdir("backend/services"))
except Exception as e:
    print("Error listing backend/services:", e)

try:
    print("Contents of backend:", os.listdir("backend"))
except Exception as e:
    print("Error listing backend:", e)
