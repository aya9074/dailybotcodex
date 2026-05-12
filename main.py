import logging
import time
from typing import Optional

import requests

from ai_parser import parse_command
from reminders import add_reminder, delete_reminder, render_reminders
from bot_texts import (
    EMOJI,
    help_text,
    ping_text,
    random_loading_phrase,
    start_text,
    unknown_command_text,
)
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_POLL_TIMEOUT

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


def handle_message(message_text: str) -> str:
    """Обрабатывает сообщение от пользователя и возвращает ответ"""
    message_text = message_text.strip()

    # Команды /something
    if message_text.startswith("/"):
        command = message_text.split()[0].lower()
        if command == "/start":
            return start_text()
        if command == "/ping":
            return ping_text()
        if command in {"/help", "/commands"}:
            return help_text()
        if command == "/status":
            return render_reminders()
        return unknown_command_text()

    # AI-парсинг для напоминаний
    command = parse_command(message_text)
    action = command.get("action")

    if action == "ADD_REMINDER":
        text = command.get("text", "").strip()
        if not text:
            return f"{EMOJI['search']} Не вижу текста для напоминания. Напиши: добавь в напоминания ..."
        reminder_id = add_reminder(text)
        return f"{EMOJI['ok']} Напоминание #{reminder_id} добавлено\n\n{render_reminders()}"

    if action == "DELETE_REMINDER":
        try:
            reminder_id = int(command.get("id", 0))
        except (ValueError, TypeError):
            reminder_id = 0
        if reminder_id <= 0:
            return f"{EMOJI['search']} Укажи номер для удаления. Пример: удали напоминание 2"
        deleted = delete_reminder(reminder_id)
        if deleted:
            return f"{EMOJI['delete']} Напоминание #{reminder_id} удалено\n\n{render_reminders()}"
        return f"{EMOJI['search']} Напоминание #{reminder_id} не найдено\n\n{render_reminders()}"

    if action == "LIST_REMINDERS":
        return render_reminders()

    # Обычное сообщение — показываем вдохновение + список напоминаний
    return f"{random_loading_phrase()}\n\n{render_reminders()}"


def run():
    tg = TelegramClient(TELEGRAM_BOT_TOKEN)
    offset: Optional[int] = None
    logger.info("Бот запущен (long polling)")

    while True:
        try:
            data = tg.get_updates(offset=offset)

            if not data.get("ok"):
                logger.warning("Telegram вернул ошибку: %s", data)
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

                response = handle_message(str(text))
                tg.send_message(int(chat_id), response)

        except requests.RequestException as err:
            logger.error("Ошибка сети/API: %s", err)
            time.sleep(3)
        except Exception:
            logger.exception("Неожиданная ошибка в цикле")
            time.sleep(3)


if __name__ == "__main__":
    run()
