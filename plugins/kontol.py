
from pyrogram import Client, filters
from pyrogram.types import Message

@app.on_message(filters.command(["kimak"], prefixes=[".", "/"]))
async def user_info(client: Client, message: Message):
    try:
        target = None
        if message.reply_to_message:
            target = message.reply_to_message.from_user
        elif len(message.command) > 1:
            arg = message.command[1]
            try:
                if arg.startswith("@"):
                    target = await client.get_users(arg)
                else:
                    target = await client.get_users(int(arg))
            except Exception as e:
                await message.reply_text(f"❌ Gagal mendapatkan info: {e}")
                return
        else:
            target = message.from_user
        user_id = target.id
        first_name = target.first_name or "-"
        last_name = target.last_name or "-"
        username = f"@{target.username}" if target.username else "-"
        dc_id = getattr(target, "dc_id", "Tidak diketahui")
        premium = "✅ Ya" if getattr(target, "is_premium", False) else "❌ Tidak"
        scam = "⚠️ Ya" if getattr(target, "is_scam", False) else "Tidak"
        fake = "⚠️ Ya" if getattr(target, "is_fake", False) else "Tidak"
        restricted = "🚫 Ya" if getattr(target, "is_restricted", False) else "Tidak"

        text = (
            f"🧩 **User Info**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Nama:** {first_name} {last_name}\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"🔗 **Username:** {username}\n"
            f"🌐 **DC ID:** {dc_id}\n"
            f"💎 **Premium:** {premium}\n"
            f"⚠️ **Fake:** {fake}\n"
            f"🚫 **Restricted:** {restricted}\n"
            f"🧨 **Scam:** {scam}\n"
          )

        return await message.reply_text(text, quote=True)

    except Exception as e:
        return await message.reply_text(f"❌ Error: {e}")
