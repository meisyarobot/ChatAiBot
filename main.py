"""
CHAT AI BOT: MEISYAROBOT
Repo: https://github.com/meisyarobot/ChatAiBot
"""

import os
import sys
import json
import asyncio
import signal
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

app = Client(
    "ChatAiBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

app.data = load_data()
app.ai_active = load_status()
app.config = {"DEV": DEV, "OWNER": OWNER}

import importlib

def load_plugins():
    sys.path.append(os.path.abspath("."))

    folder = "plugins"
    folder_path = os.path.abspath(folder)
    if not os.path.exists(folder_path):
        print(f"⚠️ Folder {folder} tidak ditemukan, dilewati")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith(".py") and filename != "__init__.py":
            moduleref = f"{folder}.{filename[:-3]}"
            try:
                mod = importlib.import_module(moduleref)
                if hasattr(mod, "register") and callable(mod.register):
                    mod.register(app)
                    print(f"✅ Plugin dimuat: {folder}/{filename}")
                else:
                    print(f"⚠️ Plugin {folder}/{filename} tidak memiliki fungsi register(), dilewati")
            except Exception as e:
                print(f"❌ Gagal memuat {folder}/{filename}: {e}")

from pyrogram import filters
from pyrogram.types import Message

@app.on_message(filters.user(OWNER) & filters.command("update", prefixes=[".", "/"]))
async def update_and_restart(_, msg: Message):
    await msg.reply_text("🔄 Sedang melakukan update repo utama...")
    try:
        update_main_repo()
        await msg.reply_text("✅ Update selesai, bot akan restart...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        await msg.reply_text(f"❌ Terjadi kesalahan saat update: {e}")


async def notify_owner(app):
    try:
        await app.send_message(OWNER, "🤖 Bot berhasil dihidupkan dan plugin sudah diperbarui.")
        print(f"📩 Notifikasi dikirim ke {OWNER}")
    except Exception as e:
        print(f"⚠️ Gagal mengirim notifikasi ke {OWNER}: {e}")


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
    load_plugins()
    print("✅ Semua plugin dimuat. Bot sedang berjalan...")

    try:
        app.run()
    except KeyboardInterrupt:
        print("🛑 Bot dimatikan paksa.")
