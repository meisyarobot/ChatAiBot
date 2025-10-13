"""
CHAT AI BOT: MEISYAROBOT (https://github.com/Meisyarobot/ChatAiBot)
_____: https://t.me/boyschell
_____: https://t.me/memekcode
yang ganti atau hapus kredit pantat nya bisulan tujuh turunan
"""

import os
import sys
import json
import subprocess
import re
from dotenv import load_dotenv
from pyrogram import Client, filters, enums
from pyrogram.types import Message
import google.generativeai as genai
import psutil
import platform

load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEV = int(os.getenv("DEV"))

STATUS_FILE = "ai_status.json"
BLACKLIST_FILE = "bl_id.json"
GROUP_FILE = "group_list.json"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-001")

def load_json(path, default):
    if not os.path.exists(path):
        save_json(path, default)
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

ai_status = load_json(STATUS_FILE, {"ai_active": True})
blacklist = load_json(BLACKLIST_FILE, {"blacklist": []})
group_data = load_json(GROUP_FILE, {"groups": []})

def save_status(value: bool):
    ai_status["ai_active"] = value
    save_json(STATUS_FILE, ai_status)

def load_status() -> bool:
    return ai_status.get("ai_active", True)


def gaya_gaul(text: str) -> str:
    text = text.replace("saya", "gue").replace("aku", "gue").replace("kamu", "lu")
    text = text.replace("tidak", "nggak").replace("iya", "ya").replace("terima kasih", "makasih")
    text = text.replace("sangat", "banget").replace("sekali", "abis")
    text = text.replace("baik", "sip").replace("oke", "okedeh").replace("benar", "beneran nih?")
    return text.strip()

def get_cpu_usage_per_core():
    cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
    return cpu_usage

def get_memory_usage():
    memory = psutil.virtual_memory()
    total = memory.total
    available = memory.available
    used = memory.used
    percentage = memory.percent
    return total, available, used, percentage

def get_os_info():
    """Mengambil informasi sistem operasi."""
    os_name = platform.system()
    os_version = platform.release()
    return os_name, os_version
    
app = Client("AutoChat", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_message(filters.user(DEV) & filters.command([host], prefixes=[".", "/"]))
async def check_vps_status(client: Client, message: Message):
    chl = await message.reply("Proses")
    cpu_usage_per_core = get_cpu_usage_per_core()
    cpu_info = "Penggunaan CPU per Core:\n"
    for i, usage in enumerate(cpu_usage_per_core):
        cpu_info += f"  Core {i+1}: {usage}%\n"
    total_memory, available_memory, used_memory, memory_percentage = get_memory_usage()
    memory_info = "Penggunaan Memori:\n"
    memory_info += f"  Total: {total_memory / (1024 ** 3):.2f} GB\n"
    memory_info += f"  Terpakai: {used_memory / (1024 ** 3):.2f} GB\n"
    memory_info += f"  Tersedia: {available_memory / (1024 ** 3):.2f} GB\n"
    memory_info += f"  Persentase: {memory_percentage}%\n"
    os_name, os_version = get_os_info()
    os_info = "Sistem Operasi:\n"
    os_info += f"  Nama: {os_name}\n"
    os_info += f"  Versi: {os_version}\n"
    disk_info = "Penggunaan Disk:\n"
    total, used, free = psutil.disk_usage("/")
    disk_info += f"  Total: {total // (2**30)} GB\n"
    disk_info += f"  Terpakai: {used // (2**30)} GB\n"
    disk_info += f"  Kosong: {free // (2**30)} GB\n"
    disk_info += f"  Persentase: {psutil.disk_usage('/').percent}%\n"
    full_info = cpu_info + "\n" + memory_info + "\n" + os_info + "\n" + disk_info
    return await chl.edit(full_info)

@app.on_message(filters.command(["ask"], prefixes=[".", "/"]))
async def ask_gemini(client: Client, message: Message):
    try:
        if str(message.chat.id) in blacklist["blacklist"]:
            return

        question = message.text.split(" ", 1)
        if len(question) < 2:
            await message.reply_text("❓ Contoh: `.ask kenapa langit berwarna biru?`")
            return

        prompt = question[1]
        await message.reply_chat_action(enums.ChatAction.TYPING)

        response = model.generate_content(prompt)
        answer = getattr(response, "text", None)
        if not answer and hasattr(response, "candidates"):
            answer = response.candidates[0].content.parts[0].text

        if not answer:
            await message.reply_text("❌ Tidak ada jawaban dari AI.")
            return

        for part in [answer[i:i + 4000] for i in range(0, len(answer), 4000)]:
            await message.reply_text(part, quote=True)

        print(f"🧠 ASK by {message.from_user.first_name}: {prompt[:40]}...")

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
        print(f"Error di .ask: {e}")

@app.on_message(filters.user(DEV) & filters.command(["su"], prefixes=[".", "/"]))
async def toggle_ai(client: Client, message: Message):
    args = message.text.lower().split()

    if len(args) == 1:
        status = "🟢 hidup" if load_status() else "🔴 mati"
        await message.reply_text(f"Status AI sekarang: {status}")
        return

    cmd = args[1]
    if cmd == "on":
        save_status(True)
        await message.reply_text("🟢 AI mode aktif lagi, bro!")
        print("🟢 AI MODE: ON")
    elif cmd == "off":
        save_status(False)
        await message.reply_text("🔴 AI mode dimatiin dulu, santai.")
        print("🔴 AI MODE: OFF")


@app.on_message(filters.user(DEV) & filters.command(["bl", "unbl"], prefixes=[".", "/"]))
async def manage_blacklist(client, message: Message):
    cmd = message.command[0]
    target = None

    if message.reply_to_message:
        target = str(message.reply_to_message.from_user.id)
    elif len(message.command) > 1:
        target = message.command[1]

    if not target:
        await message.reply_text("⚠️ Harap reply pesan atau masukkan ID/username.")
        return

    if cmd == "bl":
        if target not in blacklist["blacklist"]:
            blacklist["blacklist"].append(target)
            save_json(BLACKLIST_FILE, blacklist)
            await message.reply_text(f"🚫 {target} masuk daftar blacklist.")
        else:
            await message.reply_text("❗ Sudah di blacklist.")
    elif cmd == "unbl":
        if target in blacklist["blacklist"]:
            blacklist["blacklist"].remove(target)
            save_json(BLACKLIST_FILE, blacklist)
            await message.reply_text(f"✅ {target} dihapus dari blacklist.")
        else:
            await message.reply_text("❗ Tidak ada di blacklist.")


@app.on_message(filters.user(DEV) & filters.command(["addgc", "delgc", "listgc"], prefixes=[".", "/"]))
async def manage_groups(client: Client, message: Message):
    cmd = message.command[0]
    groups = group_data["groups"]

    if cmd == "addgc":
        if message.chat.type in ["group", "supergroup"]:
            gc_id = message.chat.id
            gc_name = message.chat.title
        elif len(message.command) > 1:
            arg = message.command[1]
            try:
                if arg.startswith("-100"):
                    gc_id = int(arg)
                    gc_name = str(gc_id)
                else:
                    gc = await client.get_chat(arg)
                    gc_id = gc.id
                    gc_name = gc.title
            except Exception as e:
                await message.reply_text(f"❌ Gagal menambahkan grup: {e}")
                return
        else:
            await message.reply_text("⚠️ Gunakan `.addgc @username` atau jalankan di grup.")
            return

        if gc_id not in groups:
            groups.append(gc_id)
            save_json(GROUP_FILE, {"groups": groups})
            await message.reply_text(f"✅ Grup '{gc_name}' berhasil ditambahkan.")
        else:
            await message.reply_text("❗ Grup ini sudah ada di daftar.")

    elif cmd == "delgc":
        if message.chat.type in ["group", "supergroup"]:
            gc_id = message.chat.id
        elif len(message.command) > 1:
            gc_id = message.command[1]
        else:
            await message.reply_text("⚠️ Gunakan `.delgc @username` atau jalankan di grup.")
            return

        try:
            gc_id = int(gc_id)
        except:
            try:
                gc = await client.get_chat(gc_id)
                gc_id = gc.id
            except Exception as e:
                await message.reply_text(f"❌ Error: {e}")
                return

        if gc_id in groups:
            groups.remove(gc_id)
            save_json(GROUP_FILE, {"groups": groups})
            await message.reply_text(f"🗑️ Grup {gc_id} dihapus dari daftar.")
        else:
            await message.reply_text("❗ Grup tidak ditemukan dalam daftar.")

    elif cmd == "listgc":
        if not groups:
            await message.reply_text("📭 Belum ada grup terdaftar.")
            return
        text = "📜 **Daftar Grup Terdaftar:**\n\n"
        for i, gid in enumerate(groups, 1):
            try:
                chat = await client.get_chat(gid)
                text += f"{i}. {chat.title} (`{gid}`)\n"
            except:
                text += f"{i}. (Tidak bisa diakses) `{gid}`\n"
        await message.reply_text(text)

@app.on_message(filters.user(DEV) & filters.command(["update"], prefixes=[".", "/"]))
async def update_repo(client: Client, message: Message):
    await message.reply_text("🔄 Sedang melakukan update...")
    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        output = result.stdout + result.stderr

        if "Already up to date" in output:
            await message.reply_text("✅ Sudah versi terbaru.")
        else:
            await message.reply_text("✅ Update selesai, bot restart...")
            print("♻️ Restarting...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        await message.reply_text(f"❌ Gagal update: {e}")

@app.on_message(filters.command(["info"], prefixes=[".", "/"]))
async def user_info(client: Client, message: Message):
    try:
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
                await message.reply_text(f"❌ Gagal mendapatkan info: {e}", quote=True)
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

        await message.reply_text(text, quote=True)

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}", quote=True)

@app.on_message(filters.group & ~filters.me & ~filters.bot)
async def auto_reply(client: Client, message: Message):
    if not load_status():
        return
    if str(message.chat.id) not in [str(g) for g in group_data["groups"]]:
        return
    if str(message.from_user.id) in blacklist["blacklist"]:
        return
    if not message.text:
        return

    try:
        prompt = f"""
        Balas pesan ini kayak anak muda, santai, gaul dan kekinian.
        Maksimal 2 kalimat tanpa emoji. Jangan keliatan kayak AI.
        Pesan: {message.text}
        """

        response = model.generate_content(prompt)
        answer = getattr(response, "text", None)
        if not answer and hasattr(response, "candidates"):
            answer = response.candidates[0].content.parts[0].text

        if not answer:
            return

        jawaban = gaya_gaul(answer)
        await message.reply_text(jawaban, quote=True)
        print(f"💬 [{message.chat.title}] {message.from_user.first_name}: {message.text[:30]} → {jawaban[:40]}")

    except Exception as e:
        print(f"❌ Error auto-reply: {e}")

print(f"🤖 Userbot aktif — Mode awal: {'🟢 ON' if load_status() else '🔴 OFF'}")
app.run()
app.send_message(DEV, "BOT ON")
