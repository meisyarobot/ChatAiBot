import importlib.util
import sys
import shutil

EXTRA_REPO = "https://github.com/user/extra-plugins.git"
EXTRA_DIR = "extra_plugins"

def load_extra_plugins():
    if not os.path.exists(EXTRA_DIR):
        subprocess.run(["git", "clone", EXTRA_REPO, EXTRA_DIR])
    else:
        subprocess.run(["git", "-C", EXTRA_DIR, "pull"])

    sys.path.insert(0, os.path.abspath(EXTRA_DIR))

    for file in os.listdir(EXTRA_DIR):
        if file.endswith(".py"):
            module_name = file[:-3]
            try:
                spec = importlib.util.spec_from_file_location(
                    module_name, os.path.join(EXTRA_DIR, file)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✅ Loaded extra plugin: {module_name}")
            except Exception as e:
                print(f"⚠️ Gagal load {file}: {e}")


if __name__ == "__main__":
    load_extra_plugins()
    print("🚀 Bot aktif dengan extra plugins!")
    app.run()

