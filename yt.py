import os
import asyncio
from yt_dlp import YoutubeDL
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from youtubesearchpython import VideosSearch

COOKIES_FILE = "cookies.txt"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def safe_download(url, fmt):
    """Proses yt-dlp dengan fallback jika error proxies"""
    base_opts = {
        "cookiefile": COOKIES_FILE,
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }
    if fmt == "mp3":
        base_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        base_opts.update({
            "format": "best[ext=mp4]/best",
            "merge_output_format": "mp4",
        })

    try:
        with YoutubeDL(base_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if fmt == "mp3":
                file_path = os.path.splitext(file_path)[0] + ".mp3"
            return info, file_path
    except TypeError as e:
        if "proxies" in str(e):
            print("[!] Fallback aktif — hapus argumen proxies")
            clean_opts = {k: v for k, v in base_opts.items() if k != "proxies"}
            with YoutubeDL(clean_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if fmt == "mp3":
                    file_path = os.path.splitext(file_path)[0] + ".mp3"
                return info, file_path
        else:
            raise e
