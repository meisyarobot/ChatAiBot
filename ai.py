import os
from io import BytesIO
from PIL import Image
from pyrogram import Client, filters
from dotenv import load_dotenv
import hashlib
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("AIzaSyAZF0QvLu6cfKNH22mJgQTXSrb1Mbp6q3Q")

client = genai.Client(api_key=AIzaSyAZF0QvLu6cfKNH22mJgQTXSrb1Mbp6q3Q)
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def generate_image(prompt: str):
    hash_name = hashlib.md5(prompt.encode()).hexdigest()
    cached_file = os.path.join(CACHE_DIR, f"{hash_name}.png")
    if os.path.exists(cached_file):
        return cached_file
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt]
    )
    
    try:
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(cached_file)
                return cached_file
    except Exception as e:
        print("Error generating image:", e)
        return None
