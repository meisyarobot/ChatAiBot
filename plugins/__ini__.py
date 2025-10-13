import os
import sys
import importlib

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

for filename in os.listdir(os.path.dirname(__file__)):
    if filename.endswith(".py") and filename != "__init__.py":
        modulename = filename[:-3]
        try:
            importlib.import_module(f"plugins.{modulename}")
            print(f"✅ Plugin dimuat: plugins/{filename}")
        except Exception as e:
            print(f"⚠️ Gagal memuat plugins/{filename}: {e}")
