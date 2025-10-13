from pyrogram import Client, filters
from pyrogram.types import Message
import json
import os

from main import app 

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data({"blacklist": [], "allowed_groups": []})
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()
DEV = int(os.getenv("DEV", 0))


@app.on_message(filters.user(DEV) & filters.command(["addbl", "delbl", "listbl"], prefixes=[".", "/"]))
async def manage_blacklist(_, msg: Message):
    cmd = msg.command[0]
    args = msg.command[1:] if len(msg.command) > 1 else []

    user_id = None
    if msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
    elif args:
        arg = args[0]
        try:
            if arg.startswith("@"):
                user = await app.get_users(arg)
                user_id = user.id
            else:
                user_id = int(arg)
        except:
            return await msg.reply_text("❌ Tidak bisa menemukan user itu.")

    if cmd == "addbl":
        if not user_id:
            return await msg.reply_text("⚠️ Gunakan reply user atau masukkan id/@username")
        if user_id not in data["blacklist"]:
            data["blacklist"].append(user_id)
            save_data(data)
            await msg.reply_text(f"🚫 User `{user_id}` ditambahkan ke blacklist.")
        else:
            await msg.reply_text("⚠️ User sudah di blacklist.")

    elif cmd == "delbl":
        if not user_id:
            return await msg.reply_text("⚠️ Gunakan reply user atau masukkan id/@username")
        if user_id in data["blacklist"]:
            data["blacklist"].remove(user_id)
            save_data(data)
            await msg.reply_text(f"✅ User `{user_id}` dihapus dari blacklist.")
        else:
            await msg.reply_text("❌ User tidak ada di blacklist.")

    elif cmd == "listbl":
        if not data["blacklist"]:
            return await msg.reply_text("📭 Tidak ada user di blacklist.")
        text = "🚫 **Daftar Blacklist:**\n"
        for uid in data["blacklist"]:
            try:
                user = await app.get_users(uid)
                name = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={uid})"
                text += f"- {name}\n"
            except:
                text += f"- `{uid}` (tidak diketahui)\n"
        await msg.reply_text(text, disable_web_page_preview=True)


@app.on_message(filters.user(DEV) & filters.command(["addgc", "delgc", "listgc"], prefixes=[".", "/"]))
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
