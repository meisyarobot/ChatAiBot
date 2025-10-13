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
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROUP_TARGET = int(os.getenv("GROUP_TARGET", "0"))
DEV = int(os.getenv("DEV", "0"))
OWNER = os.getenv("OWNER", "@boyschell")

EXTRA_PLUGIN_REPO = "https://github.com/meisyarobot/extra-plugins"
EXTRA_PLUGIN_DIR = "extra_plugins"
DATA_FILE = "data.json"
STATUS_FILE = "status.json"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5")

app = Client("ChatAiBot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)


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

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_status():
    data = load_json(STATUS_FILE, {"ai_active": True})
    return data.get("ai_active", True)

def save_status(value: bool):
    save_json(STATUS_FILE, {"ai_active": value})

def load_data():
    return load_json(DATA_FILE, {"allowed_groups": [], "blacklist": []})

def save_data(data):
    save_json(DATA_FILE, data)


ai_active = load_status()
data = load_data()


def run_command(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode().strip()

def update_repo(path, repo_url):
    if os.path.exists(path):
        print(f"🗑️ Menghapus folder lama {path}...")
        shutil.rmtree(path)

    print(f"📦 Clone repo baru dari {repo_url} ke {path}...")
    result = run_command(f"git clone {repo_url} {path}")
    print(result)

def auto_update_all():
    update_main_repo()
    print("🔁 Mengecek update extra-plugins...")
    update_repo(EXTRA_PLUGIN_DIR, EXTRA_PLUGIN_REPO)

def load_plugins():
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


@app.on_message(filters.chat(GROUP_TARGET) & ~filters.me & ~filters.bot)
async def reply_with_gemini(_, message: Message):
    global ai_active

    if not load_status():
        return

    user = message.from_user
    if not user or user.is_bot:
        return

    if user.id in data["blacklist"]:
        print(f"🚫 {user.first_name} diblacklist, di-skip.")
        return

    if data["allowed_groups"] and message.chat.id not in data["allowed_groups"]:
        print(f"🚷 Grup {message.chat.title} belum di-whitelist.")
        return

    try:
        user_text = message.text
        if not user_text:
            return

        await message.reply_chat_action(enums.ChatAction.TYPING)

        prompt = f"""
        Balas pesan ini kayak anak muda, santai, gaul dan kekinian.
        Maksimal 2 kalimat tanpa emoji.
        Pesan: {user_text}
        """

        response = model.generate_content(prompt)
        answer = getattr(response, "text", None) or response.candidates[0].content.parts[0].text
        jawaban_gaul = gaya_gaul(answer)
        await message.reply_text(jawaban_gaul, quote=True)

        print(f"💬 [{message.from_user.first_name}] {user_text} → {jawaban_gaul}")

    except Exception as e:
        print(f"❌ Error: {e}")


@app.on_message(filters.user(DEV) & filters.command(["addgc", "delgc", "listgc"], [".", "/"]))
async def manage_groups(_, msg: Message):
    cmd = msg.command[0]
    args = msg.command[1:] if len(msg.command) > 1 else []

    if cmd == "addgc":
        chat_id = msg.chat.id if not args else int(args[0]) if args[0].isdigit() else None
        if chat_id and chat_id not in data["allowed_groups"]:
            data["allowed_groups"].append(chat_id)
            save_data(data)
            await msg.reply_text(f"✅ Grup `{chat_id}` ditambahkan ke whitelist.")
        else:
            await msg.reply_text("⚠️ Grup sudah ada di whitelist atau ID tidak valid.")

    elif cmd == "delgc":
        chat_id = msg.chat.id if not args else int(args[0]) if args[0].isdigit() else None
        if chat_id in data["allowed_groups"]:
            data["allowed_groups"].remove(chat_id)
            save_data(data)
            await msg.reply_text(f"🗑️ Grup `{chat_id}` dihapus dari whitelist.")
        else:
            await msg.reply_text("❌ Grup tidak ditemukan di whitelist.")

    elif cmd == "listgc":
        if not data["allowed_groups"]:
            await msg.reply_text("📭 Tidak ada grup yang diizinkan.")
            return

        text = "📜 **Daftar Grup yang Diizinkan:**\n"
        for gc_id in data["allowed_groups"]:
            try:
                chat = await app.get_chat(gc_id)
                link = chat.invite_link or f"tg://resolve?domain={chat.username}" if chat.username else "-"
                text += f"- **{chat.title}** → {link}\n"
            except:
                text += f"- `{gc_id}` (tidak diketahui)\n"

        await msg.reply_text(text)

@app.on_message(filters.user(DEV) & filters.command(["addbl", "delbl", "listbl"], [".", "/"]))
async def manage_blacklist(_, msg: Message):
    cmd = msg.command[0]
    args = msg.command[1:] if len(msg.command) > 1 else []

    user_id = None

    if msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
    elif args:
        arg = args[0]
        if arg.isdigit():
            user_id = int(arg)
        elif arg.startswith("@"):
            try:
                user = await app.get_users(arg)
                user_id = user.id
            except:
                return await msg.reply_text("❌ Tidak bisa menemukan user itu.")

    if not user_id:
        return await msg.reply_text("⚠️ Gunakan `.addbl replyuser` atau `.addbl <id/@username>`")

    if cmd == "addbl":
        if user_id not in data["blacklist"]:
            data["blacklist"].append(user_id)
            save_data(data)
            await msg.reply_text(f"🚫 User `{user_id}` ditambahkan ke blacklist.")
        else:
            await msg.reply_text("⚠️ User sudah di blacklist.")

    elif cmd == "delbl":
        if user_id in data["blacklist"]:
            data["blacklist"].remove(user_id)
            save_data(data)
            await msg.reply_text(f"✅ User `{user_id}` dihapus dari blacklist.")
        else:
            await msg.reply_text("❌ User tidak ditemukan di blacklist.")

    elif cmd == "listbl":
        if not data["blacklist"]:
            await msg.reply_text("📭 Tidak ada user di blacklist.")
            return

        text = "🚫 **Daftar Blacklist:**\n"
        for uid in data["blacklist"]:
            try:
                user = await app.get_users(uid)
                link = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={uid})"
                text += f"- {link}\n"
            except:
                text += f"- `{uid}` (tidak diketahui)\n"

        await msg.reply_text(text, disable_web_page_preview=True)

async def notify_owner():
    try:
        await app.send_message(OWNER, "🤖 Bot berhasil dihidupkan dan plugin sudah diperbarui.")
        print(f"📩 Notifikasi dikirim ke {OWNER}")
    except Exception as e:
        print(f"⚠️ Gagal mengirim notifikasi ke {OWNER}: {e}")


@app.on_message(filters.user(DEV) & filters.command(["update"], [".", "/"]))
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
