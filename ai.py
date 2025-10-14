import os
import requests
from pyrogram import Client, filters
from dotenv import load_dotenv
import hashlib

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = "https://api.gemini.com/v1/images/generate"
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def generate_image(prompt: str):
    hash_name = hashlib.md5(prompt.encode()).hexdigest()
    cached_file = os.path.join(CACHE_DIR, f"{hash_name}.png")
    if os.path.exists(cached_file):
        return cached_file
    
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
        image_url = data.get("image_url")
        if image_url:
            img_data = requests.get(image_url).content
            with open(cached_file, "wb") as f:
                f.write(img_data)
            return cached_file
        elif "image_base64" in data:
            import base64
            image_bytes = base64.b64decode(data["image_base64"])
            with open(cached_file, "wb") as f:
                f.write(image_bytes)
            return cached_file
    return None
