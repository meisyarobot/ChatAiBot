import os
import sys
import importlib
import subprocess
from pyrogram import Client, filters
from dotenv import load_dotenv
import time
import json

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROUP_TARGET = int(os.getenv("GROUP_TARGET"))
DEV = int(os.getenv("DEV"))
EXTRA_PLUGIN_REPO = "https://github.com/meisyarobot/extra-plugins"
EXTRA_PLUGIN_DIR = "extra_plugins"

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


def run_command(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode().strip()

def update_repo(path, repo_url):
    if not os.path.exists(path):
        print(f"📦 Clone repo {repo_url}...")
        print(run_command(f"git clone {repo_url} {path}"))
    else:
        print(f"🔄 Update repo di {path}...")
        print(run_command(f"cd {path} && git pull"))

def restart_bot():
    print("♻️ Restarting bot...")
    os.execv(sys.executable, ['python3'] + sys.argv)

def auto_update_all():
    """Auto update repositori utama (DEV only) dan extra-plugins"""
    if os.geteuid() == 0 or True:
        print("🔁 Mengecek update extra-plugins...")
        update_repo(EXTRA_PLUGIN_DIR, EXTRA_PLUGIN_REPO)
    else:
        print("⛔ Tidak ada izin untuk update repo utama.")

def load_plugins():
    """Muat semua plugin dari folder 'plugins' dan 'extra_plugins'"""
    for folder in ["plugins", EXTRA_PLUGIN_DIR]:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            if filename.endswith(".py"):
                modulename = filename[:-3]
                try:
                    importlib.import_module(f"{folder.replace('/', '.')}.{modulename}")
                    print(f"✅ Plugin dimuat: {folder}/{filename}")
                except Exception as e:
                    print(f"⚠️ Gagal memuat {folder}/{filename}: {e}")

@app.on_message(filters.command(["start", "alive"], [".", "/"]))
async def start_message(_, msg):
    if msg.from_user.id == DEV:
        await msg.reply("✅ Bot aktif dan siap digunakan!")
    else:
        await msg.reply("🤖 Bot aktif!")


if __name__ == "__main__":
    print("🚀 Menjalankan bot...")
    auto_update_all()
    load_plugins()
    print("✅ Semua plugin dimuat. Bot sedang berjalan...")

    try:
        app.start()
        app.send_message(DEV, "🤖 Bot berhasil dihidupkan dan plugin sudah diperbarui.")
        app.idle()
    except Exception as e:
        print(f"❌ Error saat menjalankan bot: {e}")
