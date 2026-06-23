import os
import sys

backend_dir = "/Users/piyushisinghal/Downloads/FixForesight/backend"
print("os.listdir(backend_dir):", os.listdir(backend_dir))
services_dir = os.path.join(backend_dir, "services")
print("Does services exist?", os.path.exists(services_dir))
print("os.listdir(services_dir):", os.listdir(services_dir))

sys.path.insert(0, "/Users/piyushisinghal/Downloads/FixForesight")
import backend
print("backend.__path__:", backend.__path__)
import pkgutil
print("Submodules:")
for m in pkgutil.iter_modules(backend.__path__):
    print("  -", m.name, "ispkg:", m.ispkg)
