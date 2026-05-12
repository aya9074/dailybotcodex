import os
from pathlib import Path
from dotenv import load_dotenv  # <-- ДОБАВИТЬ ЭТУ СТРОКУ

# ЗАГРУЖАЕМ ИЗ .env ФАЙЛА
load_dotenv()  # <-- ЭТА СТРОКА

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

# Добавляем пароль для бота
BOT_PASSWORD = os.environ.get("BOT_PASSWORD", "").strip()

BASE_DIR = Path(__file__).resolve().parent
raw_reminders_file = os.environ.get("REMINDERS_FILE", "reminders.json").strip()
REMINDERS_FILE = str((BASE_DIR / raw_reminders_file).resolve())

# Long polling timeout
TELEGRAM_POLL_TIMEOUT = int(os.environ.get("TELEGRAM_POLL_TIMEOUT", "30"))
