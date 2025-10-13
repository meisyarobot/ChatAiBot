import json
from pyrogram import Client, filters, enums
from pyrogram.types import Message
import google.generativeai as genai
import os
import re

API_ID = #ISI TANPA KUTIP
API_HASH = "" #ISI DI DALAM KUTIP
SESSION_STRING = "" #ISI DI DALAM KUTIP (Ambil session di @MissKatyBot atau t.me/MissKatyBot) [USER]
GEMINI_API_KEY = "" #ISI DI DALAM KUTIP
GROUP_TARGET =  -100 #ISI TANPA KUTIP (ID harus di awali dengan -100) GRUP YANG BISA DI AKSES BOT

DEV = #ISI TANPA KUTIP

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5")

STATUS_FILE = "ai_status.json"


def load_status():
    """Baca status dari JSON."""
    if not os.path.exists(STATUS_FILE):
        save_status(True)
    with open(STATUS_FILE, "r") as f:
        data = json.load(f)
    return data.get("ai_active", True)


def save_status(value: bool):
    """Simpan status ke JSON."""
    with open(STATUS_FILE, "w") as f:
        json.dump({"ai_active": value}, f, indent=4)

ai_active = load_status()

def gaya_gaul(text: str) -> str:
    """Ubah bahasa ke gaya gaul santai."""
    text = text.replace("saya", "gue").replace("aku", "gue").replace("kamu", "lu")
    text = text.replace("tidak", "nggak").replace("iya", "ya").replace("terima kasih", "makasih")
    text = text.replace("sangat", "banget").replace("sekali", "abis")
    text = text.replace("baik", "sip").replace("oke", "okedeh").replace("benar", "beneran nih?")
    return text.strip()


app = Client("AutoChat", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)


@app.on_message(filters.user(DEV) & filters.regex(r"^\.su", re.IGNORECASE))
async def toggle_ai(client: Client, message: Message):
    global ai_active
    text = message.text.lower().strip()

    if text == ".su on":
        ai_active = True
        save_status(True)
        await message.reply_text("oke bro gw on lagi")
        print("🟢 AI MODE: ON")

    elif text == ".su off":
        ai_active = False
        save_status(False)
        await message.reply_text("oke bro gw mati")
        print("🔴 AI MODE: OFF")

    elif text == ".su":
        ai_active = load_status()
        status = "idup" if ai_active else "mokad"
        await message.reply_text(f"Status AI sekarang: {status}")
        print(f"📘 Status diminta: {status}")


@app.on_message(filters.chat(GROUP_TARGET) & ~filters.me & ~filters.bot)
async def reply_with_gemini(client: Client, message: Message):
    global ai_active

    if not load_status(): 
        return

    try:
        user_text = message.text
        if not user_text:
            return

        await message.reply_chat_action(enums.ChatAction.TYPING)

        prompt = f"""
        Balas pesan ini kayak anak muda, santai, gaul dan kekininan.
        Maksimal 2 kalimat tanpa emoji. Jangan keliatan kayak AI.
        usahakan jangan memakai bahasa inggris, bro sis, dan jawaban sesingkat mungkin.
        Pesan: {user_text}
        """

        response = model.generate_content(prompt)
        answer = getattr(response, "text", None) or response.candidates[0].content.parts[0].text
        jawaban_gaul = gaya_gaul(answer)

        await message.reply_text(jawaban_gaul, quote=True)
        print(f"💬 [{message.from_user.first_name}] {user_text} → {jawaban_gaul}")

    except Exception as e:
        print(f"❌ Error: {e}")


print(f"🤖 Userbot aktif — Mode awal: {'🟢 ON' if load_status() else '🔴 OFF'}")
app.run()
