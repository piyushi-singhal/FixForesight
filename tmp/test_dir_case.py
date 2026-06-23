import os
import sys

base = "backend"
print("Folder listing for relative path:", base)
for entry in os.scandir(base):
    print(f"Name: '{entry.name}', IsDir: {entry.is_dir()}, IsFile: {entry.is_file()}")
