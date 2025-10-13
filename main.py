"""
CHAT AI BOT: MEISYAROBOT (https://github.com/Meisyarobot/ChatAiBot)
_____: https://t.me/boyschell
_____: https://t.me/memekcode
Yang ganti atau hapus kredit pantatnya bisulan tujuh turunan.
"""

import os
import sys
import importlib
import subprocess
from pyrogram import Client, filters
from dotenv import load_dotenv
import asyncio
import signal

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

app = Client(
    "ChatAiBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


def run_command(cmd: str) -> str:
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


def auto_update_all():
    """Auto update repositori utama dan extra-plugins"""
    print("🔁 Mengecek update extra-plugins...")
    update_repo(EXTRA_PLUGIN_DIR, EXTRA_PLUGIN_REPO)


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

    def _stop(*_):
        stop_event.set()

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
