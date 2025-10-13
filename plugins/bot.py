from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.command(["ping"], [".", "/"]))
async def ping_command(client: Client, message: Message):
    """Cek apakah bot hidup"""
    await message.reply_text("🏓 Pong! Bot aktif dan responsif.")

@Client.on_message(filters.command(["id"], [".", "/"]))
async def get_id(client: Client, message: Message):
    """Menampilkan ID user dan chat"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    await message.reply_text(f"👤 **User ID:** `{user_id}`\n💬 **Chat ID:** `{chat_id}`")

@Client.on_message(filters.command(["echo"], [".", "/"]))
async def echo_message(client: Client, message: Message):
    """Bot mengulang pesan"""
    if len(message.command) < 2:
        return await message.reply_text("Gunakan `.echo teksnya` untuk mencoba.")
    text = " ".join(message.command[1:])
    await message.reply_text(f"🗣️ {text}")
