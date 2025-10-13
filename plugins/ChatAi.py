from pyrogram import filters, enums
from pyrogram.types import Message
import google.generativeai as genai

def register(app):
    data = app.data
    ai_active = app.ai_active

    def gaya_gaul(text: str) -> str:
        text = text.replace("saya", "gue").replace("aku", "gue").replace("kamu", "lu")
        text = text.replace("tidak", "nggak").replace("iya", "ya").replace("terima kasih", "makasih")
        text = text.replace("sangat", "banget").replace("sekali", "abis")
        text = text.replace("baik", "sip").replace("oke", "okedeh").replace("benar", "beneran nih?")
        return text.strip()

    @app.on_message(~filters.me & ~filters.bot)
    async def chat_ai(_, message: Message):
        nonlocal data, ai_active
        user = message.from_user
        if not user or user.is_bot:
            return
        if user.id in data["blacklist"]:
            return  # skip AI response
        if message.text and message.text.startswith((".", "/")):
            return  # skip command
        if not ai_active:
            return
        if message.chat.type in ["group", "supergroup"]:
            if data["allowed_groups"] and message.chat.id not in data["allowed_groups"]:
                return
        elif message.chat.type != "private":
            return

        user_text = message.text
        if not user_text:
            return

        await message.reply_chat_action(enums.ChatAction.TYPING)
        prompt = f"""
        Balas pesan ini kayak anak muda, santai, kekinian.
        Maksimal 2 kalimat tanpa emoji. Jangan tunjukkan kalau AI. Bercanda atau logika seperti manusia.
        Pesan: {user_text}
        """
        try:
            response = model.generate_content(prompt)
            answer = getattr(response, "text", None) or response.candidates[0].content.parts[0].text
            jawaban_gaul = gaya_gaul(answer)
            await message.reply_text(jawaban_gaul, quote=True)
        except Exception as e:
            print(f"❌ Error AI: {e}")
