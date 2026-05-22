import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
BOT_PASSWORD = os.environ.get("BOT_PASSWORD", "").strip()

BASE_DIR = Path(__file__).resolve().parent
raw_reminders_file = os.environ.get("REMINDERS_FILE", "reminders.json").strip()
REMINDERS_FILE = str((BASE_DIR / raw_reminders_file).resolve())

TELEGRAM_POLL_TIMEOUT = int(os.environ.get("TELEGRAM_POLL_TIMEOUT", "30"))
