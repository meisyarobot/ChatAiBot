from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

GEMINI_API_KEY = os.getenv("AIzaSyAZF0QvLu6cfKNH22mJgQTXSrb1Mbp6q3Q")

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

client_ai = genai.Client(api_key=GEMINI_API_KEY)


def generate_image(prompt: str, output_filename: str):
    try:
        response = client_ai.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                image_size="1024x1024",
            ),
        )

        for img in response.generated_images:
            image_bytes = img.image.image_bytes
            image = Image.open(BytesIO(image_bytes))
            image.save(output_filename)
            print(f"✅ Image saved as {output_filename}")
            return output_filename

    except Exception as e:
        print("Error generating image:", e)
        return None
