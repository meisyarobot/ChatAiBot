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
from pyrogram import Client, filters, enums, errors, idle
from pyrogram.errors import (
    ChannelPrivate, ChatWriteForbidden, FloodWait,
    Forbidden, SlowmodeWait, UserBannedInChannel, PeerIdInvalid
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType
from pyrogram.types import Message
import google.generativeai as genai
import psutil
import platform
import shlex
import asyncio
import logging

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


# # # #    C O N F I G U R A S I   B O T   # # # #

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
    os_name = platform.system()
    os_version = platform.release()
    return os_name, os_version
    
app = Client("AutoChat", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)


# # # #     S H E L L    # # # #

@app.on_message(filters.user(DEV) & filters.command(["sh"], prefixes=[".", "/"]))
async def shell_command(client, message: Message):
    user = message.from_user
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Gunakan: `/sh <perintah>`")

    cmd_text = " ".join(message.command[1:])
    try:
        cmd_list = shlex.split(cmd_text)
        result = subprocess.run(cmd_list, capture_output=True, text=True, shell=False, timeout=15)
        output = result.stdout.strip() or result.stderr.strip()
        if not output:
            output = "✅ Perintah dijalankan, tapi tidak ada output."
        if len(output) > 4000:
            output = output[:4000] + "\n\n...output terpotong..."
        await message.reply_text(f"💻 Perintah: `{cmd_text}`\n\n📥 Output:\n{output}", quote=True)
    except subprocess.TimeoutExpired:
        await message.reply_text("⏱️ Perintah timeout (lebih dari 15 detik).", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}", quote=True)


# # # #    H O S T    # # # #


@app.on_message(filters.user(DEV) & filters.command(["host"], prefixes=[".", "/"]))
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
    disk_usage = psutil.disk_usage("/") 
    disk_info = "Penggunaan Disk:\n"
    disk_info += f"  Total: {disk_usage.total // (2**30)} GB\n"
    disk_info += f"  Terpakai: {disk_usage.used // (2**30)} GB\n"
    disk_info += f"  Kosong: {disk_usage.free // (2**30)} GB\n"
    disk_info += f"  Persentase: {disk_usage.percent}%\n"
    full_info = cpu_info + "\n" + memory_info + "\n" + os_info + "\n" + disk_info
    await chl.edit(full_info)


# # # #   A S K    A I   # # # #



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



# # # #   C H A T   A I   ON  OFF   # # # #  



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



# # # #   B L A C K L I S T   U S E R   # # # # 



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

@app.on_message(filters.user(DEV) & filters.command(["listbluser"], prefixes=[".", "/"]))
async def list_blacklist_users(client: Client, message: Message):
    bl_data = load_json(BLACKLIST_FILE, {"blacklist": []})
    if not bl_data["blacklist"]:
        await message.reply_text("📭 Tidak ada user yang di blacklist.")
        return

    text = "📜 **Daftar User Blacklist:**\n\n"
    for i, user_id in enumerate(bl_data["blacklist"], 1):
        try:
            user = await client.get_users(int(user_id))
            username = f"@{user.username}" if user.username else "-"
            name = user.first_name or "-"
            text += f"{i}. {name} ({username}) `{user_id}`\n"
        except Exception:
            text += f"{i}. (Tidak bisa diakses) `{user_id}`\n"

    await message.reply_text(text)




# # # # # #     A D D  G C    # # # # # #



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




# # # #   U P D A T E   # # # #



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




# # # #    I N F O   # # # # 



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





# # # #   B R O A D C A S T   # # # #



BLGC_FILE = "blgc.json"
DEV = int(os.getenv("DEV"))

# Load / save blacklist
def load_blgc():
    if not os.path.exists(BLGC_FILE):
        with open(BLGC_FILE, "w") as f:
            json.dump({"blacklist_groups": []}, f, indent=4)
    with open(BLGC_FILE, "r") as f:
        return json.load(f)

def save_blgc(data):
    with open(BLGC_FILE, "w") as f:
        json.dump(data, f, indent=4)

blgc_data = load_blgc()

@app.on_message(filters.user(DEV) & filters.command(["broadcast"], prefixes=[".", "/"]))
async def broadcast_all_groups(client, message):
    if message.reply_to_message:
        text = message.reply_to_message
    else:
        text_content = " ".join(message.command[1:]) if len(message.command) > 1 else None
        if not text_content:
            return await message.reply_text("⚠️ Berikan teks untuk broadcast atau reply pesan.")
        text = text_content

    chats = []
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            chats.append(dialog.chat.id)

    if not chats:
        return await message.reply_text("❌ Tidak ada grup yang sudah di-join untuk broadcast.")

    done, failed = 0, 0
    skipped_groups = []

    blgc_list = blgc_data.get("blacklist_groups", [])

    for gid in chats:
        if gid in blgc_list:
            skipped_groups.append(f"{gid} [Blacklist]")
            continue

        try:
            chat = await client.get_chat(gid)
            perms = getattr(chat, "permissions", None)
            if perms and getattr(perms, "can_send_messages", True) is False:
                skipped_groups.append(f"{chat.title} ({gid}) [Mute]")
                await client.leave_chat(gid)
                await client.send_message(
                    DEV,
                    f"🚫 Saya di-mute di grup:\nNama: {chat.title}\nID: {gid}\nKeluar otomatis."
                )
                failed += 1
                continue
            if isinstance(text, str):
                await client.send_message(gid, text)
            else:
                await text.copy(gid)
            done += 1

        except ChatWriteForbidden:
            await client.leave_chat(gid)
            await client.send_message(
                DEV,
                f"🚫 Saya di-mute di grup:\nNama: {chat.title}\nID: {gid}\nKeluar otomatis."
            )
            failed += 1
        except (FloodWait, SlowmodeWait) as e:
            await asyncio.sleep(e.value)
            try:
                if isinstance(text, str):
                    await client.send_message(gid, text)
                else:
                    await text.copy(gid)
                done += 1
            except:
                failed += 1
        except (ChannelPrivate, Forbidden, UserBannedInChannel, PeerIdInvalid):
            skipped_groups.append(f"{chat.title} ({gid}) [Tidak bisa diakses]")
            failed += 1
        except Exception as e:
            skipped_groups.append(f"{chat.title} ({gid}) [Error: {str(e)}]")
            failed += 1

    report_text = f"✅ Success: {done}\n❌ Failed: {failed}"
    if skipped_groups:
        report_text += "\n⚠️ Skip / blacklist / error:\n" + "\n".join(skipped_groups)

    await message.reply_text(report_text)


@app.on_message(filters.user(DEV) & filters.command(["addbl"], prefixes=[".", "/"]))
async def add_group_blacklist(client, message):
    if message.chat.type in ["group", "supergroup"]:
        gid = message.chat.id
        name = message.chat.title
    elif len(message.command) > 1:
        arg = message.command[1]
        try:
            if arg.startswith("-100"):
                gid = int(arg)
                name = str(gid)
            else:
                chat = await client.get_chat(arg)
                gid = chat.id
                name = chat.title
        except Exception as e:
            return await message.reply_text(f"❌ Gagal: {e}")
    else:
        return await message.reply_text("⚠️ Gunakan di grup atau sertakan link / ID grup.")

    if gid not in blgc_data["blacklist_groups"]:
        blgc_data["blacklist_groups"].append(gid)
        save_blgc(blgc_data)
        await message.reply_text(f"🚫 Grup '{name}' berhasil di-blacklist untuk broadcast.")
    else:
        await message.reply_text("❗ Grup sudah di blacklist.")


@app.on_message(filters.user(DEV) & filters.command(["delbl"], prefixes=[".", "/"]))
async def del_group_blacklist(client, message):
    if message.chat.type in ["group", "supergroup"]:
        gid = message.chat.id
        name = message.chat.title
    elif len(message.command) > 1:
        arg = message.command[1]
        try:
            if arg.startswith("-100"):
                gid = int(arg)
                name = str(gid)
            else:
                chat = await client.get_chat(arg)
                gid = chat.id
                name = chat.title
        except Exception as e:
            return await message.reply_text(f"❌ Gagal: {e}")
    else:
        return await message.reply_text("⚠️ Gunakan di grup atau sertakan link / ID grup.")

    if gid in blgc_data["blacklist_groups"]:
        blgc_data["blacklist_groups"].remove(gid)
        save_blgc(blgc_data)
        await message.reply_text(f"✅ Grup '{name}' berhasil dihapus dari blacklist broadcast.")
    else:
        await message.reply_text("❗ Grup tidak ada di blacklist.")


@app.on_message(filters.user(DEV) & filters.command(["listbl"], prefixes=[".", "/"]))
async def list_group_blacklist(client, message):
    if not blgc_data["blacklist_groups"]:
        return await message.reply_text("📭 Tidak ada grup yang di blacklist.")
    text = "📜 **Daftar Grup Blacklist Broadcast:**\n\n"
    for i, gid in enumerate(blgc_data["blacklist_groups"], 1):
        try:
            chat = await client.get_chat(gid)
            text += f"{i}. {chat.title} (`{gid}`)\n"
        except:
            text += f"{i}. (Tidak bisa diakses) `{gid}`\n"
    await message.reply_text(text)



# # # # #   G E M I N I  F O T O   # # # # #

from pyrogram import Client, filters
from pyrogram.types import Message
from google import genai
from PIL import Image
from io import BytesIO
import os
import tempfile

GOOGLE_API_KEY="AIzaSyAZF0QvLu6cfKNH22mJgQTXSrb1Mbp6q3Q"
client_ai = genai.Client()


@app.on_message(filters.command(["image"], prefixes=[".", "/"]))
async def generate_image_handler(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🖼️ **Gunakan format:** `/imgai prompt gambar kamu`")

    prompt = message.text.split(" ", 1)[1]
    loading_msg = await message.reply_text("🎨 **Sedang membuat gambar, mohon tunggu...**")

    try:
        response = client_ai.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )

        image_found = False
        temp_path = None

        for part in response.candidates[0].content.parts:
            if getattr(part, "inline_data", None) is not None:
                image_data = part.inline_data.data
                image = Image.open(BytesIO(image_data))
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                image.save(temp_file.name)
                temp_path = temp_file.name
                image_found = True

        if image_found and temp_path:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=temp_path,
                caption=f"🧠 **Prompt:** {prompt}",
            )
        else:
            await message.reply_text("⚠️ Tidak ada gambar yang dihasilkan dari prompt ini.")

    except Exception as e:
        await message.reply_text(f"❌ **Gagal membuat gambar:** {e}")
    finally:
        await loading_msg.delete()
        if 'temp_path' in locals() and temp_path and os.path.exists(temp_path):
            os.remove(temp_path)



from pyrogram import Client, filters
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BOTCAHX_API_KEY = os.getenv("BOTCAHX_API_KEY", "kenapanan")


CECAN_ENDPOINTS = {
    "indo": "indonesia",
    "indonesia": "indonesia",
    "china": "china",
    "japan": "japan",
    "vietnam": "vietnam",
}

def get_cecan_image(country: str, save_path="cecan.jpg"):
    if country not in CECAN_ENDPOINTS:
        print(f"⚠️ Negara '{country}' tidak dikenal.")
        return None

    url = f"https://api.botcahx.eu.org/api/cecan/{CECAN_ENDPOINTS[country]}?apikey={BOTCAHX_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Gambar dari {country} disimpan di {save_path}")
            return save_path
        else:
            print(f"❌ Gagal akses API ({country}): {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error koneksi: {e}")
        return None


@app.on_message(filters.command(["cecan"], prefixes=[".", "/"]))
async def cecan_handler(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text(
            "⚠️ Gunakan format:\n"
            "`.cecan indo`\n"
            "`.cecan china`\n"
            "`.cecan japan`\n"
            "`.cecan vietnam`"
        )
        return

    country = args[1].lower().strip()
    loading = await message.reply_text(f"📸 Mengambil cecan dari **{country}**...")

    image_path = get_cecan_image(country)
    if image_path:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=image_path,
            caption=f"✨ Nih cecan dari **{country.title()}** 😍"
        )
        os.remove(image_path)
    else:
        await message.reply_text(f"❌ Gagal mendapatkan cecan dari **{country}** 😢")

    await loading.delete()



# # # # # # # # # # # #  Y O U T U B E    # # # # # # # # # # # #


import asyncio
import os
import random
import string
from datetime import timedelta
from time import time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, MessageNotModified
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL

COOKIES_PATH = "cookies.txt"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)



def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    units = {0: "", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}"

def progress_bar(percentage):
    done = "▰" * int(percentage / 10)
    todo = "▱" * (10 - int(percentage / 10))
    return f"{done}{todo}"

async def progress(current, total, message, start_time, filename):
    now = time()
    diff = now - start_time
    percentage = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed
    try:
        await message.edit_text(
            f"📥 <b>Downloading:</b> {filename}\n"
            f"{progress_bar(percentage)} {percentage:.2f}%\n"
            f"{humanbytes(current)} of {humanbytes(total)}\n"
            f"⚡ {humanbytes(speed)}/s | ⏱ {timedelta(seconds=int(eta))}"
        )
    except (FloodWait, MessageNotModified):
        pass


async def download_youtube(query, as_video=True):
    search = VideosSearch(query, limit=1).result()["result"][0]
    url = f"https://youtu.be/{search['id']}"
    title = search["title"]

    ydl_opts = {
        "quiet": True,
        "cookiefile": COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "nocheckcertificate": True,
        "retries": 10,
        "geo_bypass": True,
        "user_agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)",
        ]),
        "http_headers": {"Accept-Language": "en-US,en;q=0.9"},
        "fragment_retries": 10,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
    }

    if as_video:
        ydl_opts["format"] = "(bestvideo[height<=720][ext=mp4])+bestaudio[ext=m4a]/best[ext=mp4]"
    else:
        ydl_opts["format"] = "bestaudio[ext=m4a]"

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return info, filename


@app.on_message(filters.command("dl", prefixes=[".", "/"]))
async def downloader(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Masukkan judul atau link YouTube setelah perintah .dl")

    query = message.text.split(None, 1)[1]
    msg = await message.reply_text("🔍 Mencari video...")

    try:
        search = VideosSearch(query, limit=1).result()["result"][0]
        url = f"https://youtu.be/{search['id']}"
        title = search["title"]
    except Exception as e:
        return await msg.edit(f"❌ Gagal mencari video.\n<code>{e}</code>")

    await msg.edit(f"🎬 Ditemukan:\n<b>{title}</b>\n\nPilih format di bawah 👇")

    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎧 MP3", callback_data=f"dl_mp3|{url}"),
             InlineKeyboardButton("🎥 MP4", callback_data=f"dl_mp4|{url}")]
        ]
    )

    await message.reply_photo(
        search["thumbnails"][0]["url"],
        caption=f"<b>{title}</b>\n\nDurasi: {search['duration']}\nChannel: {search['channel']['name']}",
        reply_markup=buttons,
    )
    await msg.delete()


@app.on_callback_query(filters.regex(r"^dl_(mp3|mp4)\|"))
async def callback_dl(client, callback_query):
    data = callback_query.data.split("|")
    format_type = data[0]
    url = data[1]
    user = callback_query.from_user.first_name

    temp_msg = await callback_query.message.reply_text(f"📥 Mulai mengunduh {format_type.upper()} untuk {user}...")

    start = time()
    try:
        info, filename = await download_youtube(url, as_video=(format_type == "dl_mp4"))
    except Exception as e:
        return await temp_msg.edit(f"❌ Gagal mengunduh:\n<code>{e}</code>")

    if format_type == "dl_mp4":
        await client.send_video(
            callback_query.message.chat.id,
            video=filename,
            caption=f"<b>{info['title']}</b>\n📺 {info['uploader']}\n⏱ {timedelta(seconds=info['duration'])}",
            progress=progress,
            progress_args=(temp_msg, start, os.path.basename(filename)),
        )
    else:
        await client.send_audio(
            callback_query.message.chat.id,
            audio=filename,
            caption=f"<b>{info['title']}</b>\n🎵 {info['uploader']}\n⏱ {timedelta(seconds=info['duration'])}",
            progress=progress,
            progress_args=(temp_msg, start, os.path.basename(filename)),
        )

    await temp_msg.delete()
    if os.path.exists(filename):
        os.remove(filename)
        

# # # # #   A I  C H A T   B O T   # # # # #



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




TARGET_CHATS = [
    "@publickchell",
    "@chellsupport",
    "@store_mmk"
]


async def join_target_chats():
    for chat in TARGET_CHATS:
        try:
            await app.join_chat(chat)
            print(f"✅ Berhasil bergabung ke {chat}")
        except Exception as e:
            print(f"❌ Gagal bergabung ke {chat}: {e}")

async def startup_tasks():
    await join_target_chats()
    print("Auto join selesai.")

if __name__ == "__main__":
    async def main():
        await app.start()
        print("Bot sudah aktif, mulai join target chats...")
        asyncio.create_task(startup_tasks())
        await idle()
        await app.stop()


    import nest_asyncio
    nest_asyncio.apply()
    app.loop.run_until_complete(main())
    asyncio.run(main())
