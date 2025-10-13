from pyrogram import filters
from pyrogram.types import Message
import json, os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data({"blacklist": [], "allowed_groups": []})
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def init(app):
    data = load_data()

    @app.on_message(filters.user(app.config["DEV"]) & filters.command(["addgc","delgc","listgc"], prefixes=[".", "/"]))
    async def manage_groups(_, msg: Message):
        nonlocal data
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
                return await msg.reply_text("📭 Tidak ada grup yang diizinkan.")
            text = "📜 **Daftar Grup yang Diizinkan:**\n"
            for gc_id in data["allowed_groups"]:
                try:
                    chat = await app.get_chat(gc_id)
                    link = chat.invite_link or f"tg://resolve?domain={chat.username}" if chat.username else "-"
                    text += f"- **{chat.title}** → {link}\n"
                except:
                    text += f"- `{gc_id}` (tidak diketahui)\n"
            await msg.reply_text(text)
