from pyrogram import Client, filters
from google import genai
from PIL import Image
from io import BytesIO
import asyncio
import os

GEMINI_API_KEY = os.getenv("AIzaSyAZF0QvLu6cfKNH22mJgQTXSrb1Mbp6q3Q")

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

client_ai = genai.Client(api_key=GEMINI_API_KEY)


def generate_image(prompt: str, output_filename: str):
    response = client_ai.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        number_of_images=1,
        image_size="1024x1024",
    )

    for idx, generated_image in enumerate(response.generated_images, start=1):
        image_bytes = generated_image.image.image_bytes
        image = Image.open(BytesIO(image_bytes))
        image.save(output_filename)
        return output_filename
                image.save(cached_file)
                return cached_file
    except Exception as e:
        print("Error generating image:", e)
        return None
