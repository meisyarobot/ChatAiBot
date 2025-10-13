import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
GROUP_TARGET = int(os.getenv("GROUP_TARGET", 0))
DEV = int(os.getenv("DEV", 0))
OWNER = os.getenv("OWNER", "@boyschell")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATA_FILE = "data.json"
STATUS_FILE = "status.json"
PLUGINS_FOLDER = "plugins"
