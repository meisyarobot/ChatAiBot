import os
import sys
import json
import signal
import asyncio
import importlib
import shutil
import subprocess
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
        save_json(path, default or {})
        return default or {}

def load_status():
    return load_json(STATUS_FILE, {"ai_active": True}).get("ai_active", True)

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

app = Client("ChatAiBot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
ai_active = load_status()
data = load_data()

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

def load_plugins():
    sys.path.append(os.path.abspath("."))
    for folder in ["plugins", "extra_plugins"]:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            if filename.endswith(".py") and filename != "__init__.py":
                moduleref = f"{folder.replace('/', '.')}.{filename[:-3]}"
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
    await msg.reply("✅ Bot aktif!" if msg.from_user.id != DEV else "✅ Bot aktif dan siap digunakan!")

@app.on_message(filters.user(DEV) & filters.regex(r"^\.su", re.IGNORECASE))
async def toggle_ai(_, message: Message):
    global ai_active
    text = message.text.lower().strip()
    if text == ".su on":
        ai_active = True
        save_status(True)
        await message.reply_text("🟢 AI mode aktif.")
    elif text == ".su off":
        ai_active = False
        save_status(False)
        await message.reply_text("🔴 AI mode nonaktif.")
    elif text == ".su":
        await message.reply_text(f"📘 Status AI: {'aktif' if load_status() else 'mati'}")

@app.on_message(filters.user(OWNER) & filters.command("update", prefixes=[".", "/"]))
async def update_and_restart(_, msg: Message):
    await msg.reply_text("🔄 Melakukan update semua repo...")
    try:
        auto_update_all()
        await msg.reply_text("✅ Update selesai, bot restart...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")

async def notify_owner():
    try:
        await app.send_message(OWNER, "🤖 Bot berhasil dijalankan dan plugin dimuat.")
    except Exception as e:
        print(f"⚠️ Gagal kirim notifikasi: {e}")

@app.on_message(~filters.me & ~filters.bot)
async def main_handler(client: Client, message: Message):
    if message.text and message.text.startswith((".", "/")):
        return

    if not ai_active:
        return

    user = message.from_user
    if not user or user.is_bot or user.id in data.get("blacklist", []):
        return

    if message.chat.type in ["group", "supergroup"]:
        if data.get("allowed_groups") and message.chat.id not in data["allowed_groups"]:
            print(f"🚷 Grup {message.chat.title} belum di-whitelist.")
            return

    try:
        user_text = message.text
        if not user_text:
            return

        await message.reply_chat_action(enums.ChatAction.TYPING)
        prompt = f"""
        Balas pesan ini kayak anak muda, santai, gaul dan kekinian.
        Maksimal 2 kalimat tanpa emoji. Jangan tunjukkan kalau AI. Bercanda atau logika seperti manusia.
        Pesan: {user_text}
        """

        response = model.generate_content(prompt)
        answer = getattr(response, "text", None) or response.candidates[0].content.parts[0].text
        jawaban_gaul = gaya_gaul(answer)
        await message.reply_text(jawaban_gaul, quote=True)
        print(f"💬 [{user.first_name}] {user_text} → {jawaban_gaul}")

    except Exception as e:
        print(f"❌ Error AI: {e}")


if __name__ == "__main__":
    print("🚀 Menjalankan bot...")
    auto_update_all()
    load_plugins()
    print("✅ Semua plugin dimuat. Bot berjalan...")
    try:
        app.run()
    except KeyboardInterrupt:
        print("🛑 Bot dimatikan paksa.")
