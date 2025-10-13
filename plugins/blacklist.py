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

def register(app):
    data = load_data()

    @app.on_message(filters.user(app.config["DEV"]) & filters.command(["addbl","delbl","listbl"], prefixes=[".", "/"]))
    async def manage_blacklist(_, msg: Message):
        nonlocal data
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
