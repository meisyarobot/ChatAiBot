"""
CHAT AI BOT: MEISYAROBOT
Repo: https://github.com/meisyarobot/ChatAiBot
"""

import os
import sys
import json
import asyncio
import signal
import shutil
import subprocess
from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROUP_TARGET = int(os.getenv("GROUP_TARGET"))
DEV = int(os.getenv("DEV"))
OWNER = os.getenv("OWNER", "@boyschell")

EXTRA_PLUGIN_REPO = "https://github.com/meisyarobot/extra-plugins"
EXTRA_PLUGIN_DIR = "extra_plugins"
DATA_FILE = "data.json"
STATUS_FILE = "status.json"

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_json(path, default=None):
    if not os.path.exists(path):
        save_json(path, default or {})
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        save_json(path, default or {})
        return default or {}

def load_status():
    data = load_json(STATUS_FILE, {"ai_active": True})
    return data.get("ai_active", True)

def save_status(value: bool):
    save_json(STATUS_FILE, {"ai_active": value})

def load_data():
    return load_json(DATA_FILE, {"allowed_groups": [], "blacklist": []})

def save_data(data):
    save_json(DATA_FILE, data)

def run_command(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode().strip()

def update_main_repo():
    print("🔄 Mengecek update repo utama...")
    print(run_command("git pull"))

def update_extra_plugins():
    if os.path.exists(EXTRA_PLUGIN_DIR):
        shutil.rmtree(EXTRA_PLUGIN_DIR)
    print(f"📥 Clone ulang extra_plugins dari {EXTRA_PLUGIN_REPO}...")
    print(run_command(f"git clone {EXTRA_PLUGIN_REPO} {EXTRA_PLUGIN_DIR}"))

def auto_update_all():
    update_main_repo()
    update_extra_plugins()

async def notify_owner(app):
    try:
        await app.send_message(OWNER, "🤖 Bot berhasil dihidupkan dan plugin sudah diperbarui.")
        print(f"📩 Notifikasi dikirim ke {OWNER}")
    except Exception as e:
        print(f"⚠️ Gagal mengirim notifikasi ke {OWNER}: {e}")

app = Client(
    "ChatAiBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

app.data = load_data()
app.ai_active = load_status()
app.config = {"DEV": DEV, "OWNER": OWNER}

sys.path.append(os.path.abspath("plugins"))
try:
    import plugins
    plugins.register(app)
except Exception as e:
    print(f"⚠️ Gagal load plugins: {e}")

from pyrogram import filters
from pyrogram.types import Message

@app.on_message(filters.user(OWNER) & filters.command("update", prefixes=[".", "/"]))
async def update_and_restart(_, msg: Message):
    await msg.reply_text("🔄 Sedang melakukan update semua repo...")
    try:
        auto_update_all()
        await msg.reply_text("✅ Update selesai, bot akan restart...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        await msg.reply_text(f"❌ Terjadi kesalahan saat update: {e}")


async def runner():
    await notify_owner(app)
    print("🕒 Bot siap menerima pesan")
    
    stop_event = asyncio.Event()
    def _stop(*_): stop_event.set()
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, _stop)
        
    print("🕒 Bot sedang berjalan. Tekan Ctrl+C untuk berhenti.")
    await stop_event.wait()
    await app.stop()
    print("🛑 Bot dimatikan dengan aman.")

if __name__ == "__main__":
    print("🚀 Menjalankan bot...")
    auto_update_all()
    try:
        app.run()
    except KeyboardInterrupt:
        print("🛑 Bot dimatikan paksa.")
