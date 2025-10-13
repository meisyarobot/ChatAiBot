import os
import sys
import json
import subprocess
import importlib.util
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
import google.generativeai as genai

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROUP_TARGET = int(os.getenv("GROUP_TARGET"))
DEV = int(os.getenv("DEV"))

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

BL_FILE = "bl_id.json"
GC_FILE = "gc_list.json"
EXTRA_DIR = "extra_plugins"
EXTRA_REPO = "https://github.com/user/extra-plugins.git"


for f in [BL_FILE, GC_FILE]:
    if not os.path.exists(f):
        with open(f, "w") as x:
            json.dump([], x)


def load_extra_plugins():
    if not os.path.exists(EXTRA_DIR):
        subprocess.run(["git", "clone", EXTRA_REPO, EXTRA_DIR])
    else:
        subprocess.run(["git", "-C", EXTRA_DIR, "pull"])

    sys.path.insert(0, os.path.abspath(EXTRA_DIR))

    for file in os.listdir(EXTRA_DIR):
        if file.endswith(".py"):
            path = os.path.join(EXTRA_DIR, file)
            module_name = file[:-3]
            try:
                spec = importlib.util.spec_from_file_location(module_name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✅ Loaded extra plugin: {module_name}")
            except Exception as e:
                print(f"⚠️ Gagal load {file}: {e}")


def is_blacklisted(user_id):
    with open(BL_FILE, "r") as f:
        return user_id in json.load(f)


@app.on_message(filters.user(DEV) & filters.command(["bl"], [".", "/"]))
async def blacklist_user(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply ke user yang mau diblacklist.")
    user = message.reply_to_message.from_user
    with open(BL_FILE, "r") as f:
        bl = json.load(f)
    if user.id in bl:
        return await message.reply_text("🚫 User sudah diblacklist.")
    bl.append(user.id)
    with open(BL_FILE, "w") as f:
        json.dump(bl, f)
    await message.reply_text(f"✅ {user.first_name} telah diblacklist.")


@app.on_message(filters.user(DEV) & filters.command(["unbl"], [".", "/"]))
async def unblacklist_user(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply ke user yang mau dihapus dari blacklist.")
    user = message.reply_to_message.from_user
    with open(BL_FILE, "r") as f:
        bl = json.load(f)
    if user.id not in bl:
        return await message.reply_text("ℹ️ User tidak ada di blacklist.")
    bl.remove(user.id)
    with open(BL_FILE, "w") as f:
        json.dump(bl, f)
    await message.reply_text(f"✅ {user.first_name} dihapus dari blacklist.")


@app.on_message(filters.command(["ask"], [".", "/"]))
async def ai_reply(client, message: Message):
    if is_blacklisted(message.from_user.id):
        return
    query = message.text.split(maxsplit=1)
    if len(query) < 2:
        return await message.reply_text("❓ Gunakan: `.ask <pertanyaan>`")
    text = query[1]
    try:
        response = model.generate_content(text)
        await message.reply_text(response.text, disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text(f"⚠️ Gagal memproses: {e}")


@app.on_message(filters.user(DEV) & filters.command(["addgc"], [".", "/"]))
async def add_gc(client, message: Message):
    gc_data = message.text.split(maxsplit=1)
    if not gc_data and not message.chat:
        return await message.reply_text("Gunakan `/addgc <id atau username grup>` atau kirim langsung di grup.")

    with open(GC_FILE, "r") as f:
        gcs = json.load(f)

    if message.chat.type in ["supergroup", "group"]:
        gid = message.chat.id
        if gid not in gcs:
            gcs.append(gid)
    elif len(gc_data) > 1:
        gcs.append(gc_data[1])

    with open(GC_FILE, "w") as f:
        json.dump(gcs, f)
    await message.reply_text("✅ Grup ditambahkan ke daftar.")


@app.on_message(filters.user(DEV) & filters.command(["delgc"], [".", "/"]))
async def del_gc(client, message: Message):
    gc_data = message.text.split(maxsplit=1)
    with open(GC_FILE, "r") as f:
        gcs = json.load(f)

    target = None
    if message.chat.type in ["supergroup", "group"]:
        target = message.chat.id
    elif len(gc_data) > 1:
        target = gc_data[1]

    if target in gcs:
        gcs.remove(target)
        with open(GC_FILE, "w") as f:
            json.dump(gcs, f)
        await message.reply_text("🗑️ Grup dihapus dari daftar.")
    else:
        await message.reply_text("❌ Grup tidak ditemukan.")


@app.on_message(filters.user(DEV) & filters.command(["listgc"], [".", "/"]))
async def list_gc(client, message: Message):
    with open(GC_FILE, "r") as f:
        gcs = json.load(f)
    if not gcs:
        return await message.reply_text("ℹ️ Belum ada grup terdaftar.")
    txt = "**📋 Daftar Grup:**\n" + "\n".join([str(i) for i in gcs])
    await message.reply_text(txt)


@app.on_message(filters.user(DEV) & filters.command(["update"], [".", "/"]))
async def update_repo(client: Client, message: Message):
    await message.reply_text("🔄 Sedang melakukan update dari GitHub...")
    try:
        main_pull = subprocess.run(["git", "pull"], capture_output=True, text=True)
        extra_pull = subprocess.run(["git", "-C", EXTRA_DIR, "pull"], capture_output=True, text=True)

        output = main_pull.stdout + "\n" + extra_pull.stdout
        if "Already up to date" in output:
            await message.reply_text("✅ Tidak ada update baru.")
        else:
            await message.reply_text("✅ Update selesai, bot akan restart...")
            client.send_message(DEV, "♻️ Bot sedang restart setelah update...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        await message.reply_text(f"❌ Gagal update: {e}")


if __name__ == "__main__":
    load_extra_plugins()
    print("🚀 Bot aktif dengan extra plugins!")
    app.run()
    app.send_message(DEV, "✅ Bot sudah online kembali!")
