"""
CHAT AI BOT: MEISYAROBOT (https://github.com/Meisyarobot/ChatAiBot)
_____: https://t.me/boyschell
_____: https://t.me/memekcode
Yang ganti atau hapus kredit pantatnya bisulan tujuh turunan.
"""

import os
import sys
import re
import json
import signal
import asyncio
import importlib
import subprocess
import shutil
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from dotenv import load_dotenv
import google.generativeai as genai

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


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-001")


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
        print(f"⚠️ File {path} rusak, membuat ulang dengan default.")
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

app = Client("ChatAiBot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)


ai_active = load_status()
data = load_data()

def run_command(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode().strip()

def update_extra_plugins():
    if os.path.exists(EXTRA_PLUGIN_DIR):
        try:
            print(f"🗑️ Menghapus folder {EXTRA_PLUGIN_DIR} lama...")
            shutil.rmtree(EXTRA_PLUGIN_DIR)
        except Exception as e:
            print(f"⚠️ Gagal menghapus folder lama: {e}")
            return
    try:
        print(f"📥 Clone ulang extra_plugins dari {EXTRA_PLUGIN_REPO}...")
        result = run_command(f"git clone {EXTRA_PLUGIN_REPO} {EXTRA_PLUGIN_DIR}")
        print(result)
    except Exception as e:
        print(f"❌ Clone gagal: {e}")
        raise

def update_main_repo():
    print("🔄 Mengecek update repo utama...")
    result = run_command(f"git pull")
    print(result)

def auto_update_all():
    update_main_repo()
    update_extra_plugins()

def load_plugins():
    import importlib
    import os
    import sys
    sys.path.append(os.path.abspath("."))

    for folder in ["plugins", "extra_plugins"]:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            if filename.endswith(".py"):
                modulename = filename[:-3]
                moduleref = f"{folder.replace('/', '.')}.{modulename}"
                try:
                    mod = importlib.import_module(moduleref)
                    if hasattr(mod, "register"):
                        mod.register(app)
                    print(f"✅ Plugin dimuat: {folder}/{filename}")
                except Exception as e:
                    print(f"⚠️ Gagal memuat {folder}/{filename}: {e}")



def gaya_gaul(text: str) -> str:
    text = text.replace("saya", "gue").replace("aku", "gue").replace("kamu", "lu")
    text = text.replace("tidak", "nggak").replace("iya", "ya").replace("terima kasih", "makasih")
    text = text.replace("sangat", "banget").replace("sekali", "abis")
    text = text.replace("baik", "sip").replace("oke", "okedeh").replace("benar", "beneran nih?")
    return text.strip()

@app.on_message(filters.command(["start", "alive"], [".", "/"]))
async def start_message(_, msg):
    if msg.from_user.id == DEV:
        await msg.reply("✅ Bot aktif dan siap digunakan!")
    else:
        await msg.reply("🤖 Bot aktif!")

@app.on_message(filters.user(DEV) & filters.regex(r"^\.su", re.IGNORECASE))
async def toggle_ai(_, message: Message):
    global ai_active
    text = message.text.lower().strip()
    if text == ".su on":
        ai_active = True
        save_status(True)
        await message.reply_text("🟢 AI mode aktif lagi bro.")
    elif text == ".su off":
        ai_active = False
        save_status(False)
        await message.reply_text("🔴 AI mode dimatiin dulu bro.")
    elif text == ".su":
        status = "idup" if load_status() else "mokad"
        await message.reply_text(f"📘 Status AI sekarang: {status}")

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

async def notify_owner():
    try:
        await app.send_message(OWNER, "🤖 Bot berhasil dihidupkan dan plugin sudah diperbarui.")
        print(f"📩 Notifikasi dikirim ke {OWNER}")
    except Exception as e:
        print(f"⚠️ Gagal mengirim notifikasi ke {OWNER}: {e}")
        
async def runner():
    await app.start()
    await notify_owner()
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
    load_plugins()
    print("✅ Semua plugin dimuat. Bot sedang berjalan...")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner())
