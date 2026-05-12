# main.py
import logging
import time
from typing import Optional

import requests

from ai_parser import process_with_ai
from reminders import render_reminders
from bot_texts import (
    help_text,
    ping_text,
    random_loading_phrase,
    start_text,
    unknown_command_text,
)
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_POLL_TIMEOUT, BOT_PASSWORD
from auth import is_authorized, authorize_user

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("daily_bot")

class TelegramClient:
    def __init__(self, token: str):
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")
        self.base_url = f"https://api.telegram.org/bot{token}"

    def get_updates(self, offset: Optional[int] = None):
        payload = {"timeout": TELEGRAM_POLL_TIMEOUT, "allowed_updates": ["message"]}
        if offset is not None:
            payload["offset"] = offset
        response = requests.get(
            f"{self.base_url}/getUpdates",
            params=payload,
            timeout=TELEGRAM_POLL_TIMEOUT + 10,
        )
        response.raise_for_status()
        return response.json()

    def send_message(self, chat_id: int, text: str):
        response = requests.post(
            f"{self.base_url}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=30,
        )
        response.raise_for_status()

def handle_message(message_text: str, chat_id: int) -> str:
    msg = message_text.strip()
    
    # Парольная защита
    if not is_authorized(chat_id):
        if msg == BOT_PASSWORD:
            authorize_user(chat_id, msg, BOT_PASSWORD)
            return "✅ Доступ разрешён. Добро пожаловать, Госпожа!"
        return "🔒 Доступ запрещён. Введи пароль."
    
    # Команды /something
    if msg.startswith("/"):
        cmd = msg.split()[0].lower()
        if cmd == "/start":
            return start_text()
        if cmd == "/ping":
            return ping_text()
        if cmd in {"/help", "/commands"}:
            return help_text()
        if cmd == "/status":
            return render_reminders()
        return unknown_command_text()
    
    # Основная AI-обработка
    ai_result = process_with_ai(msg, chat_id)
    if ai_result:
        return ai_result
    
    # Если AI не ответил
    return f"{random_loading_phrase()}\n\n{render_reminders()}"

def run():
    tg = TelegramClient(TELEGRAM_BOT_TOKEN)
    offset: Optional[int] = None
    logger.info("🔥 Бот запущен (пароль + AI)")

    while True:
        try:
            data = tg.get_updates(offset=offset)
            if not data.get("ok"):
                logger.warning("Telegram ошибка")
                time.sleep(2)
                continue

            for item in data.get("result", []):
                offset = item["update_id"] + 1
                message = item.get("message")
                if not message:
                    continue
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text")
                if not chat_id or text is None:
                    continue
                response = handle_message(str(text), int(chat_id))
                tg.send_message(int(chat_id), response)

        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(3)

if __name__ == "__main__":
    run()
