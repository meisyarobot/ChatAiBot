import os
import requests
from pyrogram import Client, filters
from dotenv import load_dotenv

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = "https://api.gemini.com/v1/images/generate"

def generate_image(prompt: str):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "size": "1024x1024"
    }
    response = requests.post(GEMINI_URL, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Asumsi API mengembalikan URL gambar di data["image_url"]
        return data.get("image_url")
    else:
        return None
