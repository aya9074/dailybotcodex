import logging
import time
import threading
from typing import Optional

import requests
import schedule

from ai_parser import process_with_ai
from reminders import render_reminders
from bot_texts import help_text, ping_text, start_text, unknown_command_text, random_loading_phrase
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_POLL_TIMEOUT, BOT_PASSWORD
from auth import is_authorized, authorize_user
from tasks import get_today_task, get_today_day_name, get_postponed_task, set_postponed_task, clear_postponed_task

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("daily_bot")

class TelegramClient:
    def __init__(self, token: str):
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.chat_id = None

    def get_updates(self, offset: Optional[int] = None):
        payload = {"timeout": TELEGRAM_POLL_TIMEOUT, "allowed_updates": ["message"]}
        if offset is not None:
            payload["offset"] = offset
        response = requests.get(f"{self.base_url}/getUpdates", params=payload, timeout=TELEGRAM_POLL_TIMEOUT + 10)
        response.raise_for_status()
        return response.json()

    def send_message(self, chat_id: int, text: str):
        response = requests.post(f"{self.base_url}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=30)
        response.raise_for_status()
        return response

    def set_chat_id(self, chat_id: int):
        if not self.chat_id:
            self.chat_id = chat_id

telegram_client = None

def send_daily_report():
    global telegram_client
    if not telegram_client or not telegram_client.chat_id:
        logger.warning("Нет chat_id для отправки")
        return

    today_task = get_today_task()
    day_name = get_today_day_name()
    postponed = get_postponed_task()
    
    # Получаем список активных напоминаний
    from reminders import render_reminders
    reminders_text = render_reminders()
    
    text = f"🔔 *{day_name.capitalize()}, 13:00*\n\n"
    if postponed:
        text += f"⏩ Перенесённая задача: {postponed}\n"
        clear_postponed_task()
    if today_task:
        text += f"📌 Задача дня: {today_task}\n\n"
    else:
        text += "🎉 Сегодня выходной! Но ты всё равно можешь делать контент.\n\n"
    
    text += f"{reminders_text}\n\n"
    text += "Ты делаешь это ради себя. Не останавливайся."
    
    telegram_client.send_message(telegram_client.chat_id, text)

def schedule_daily():
    schedule.every().day.at("13:00").do(send_daily_report)
    while True:
        schedule.run_pending()
        time.sleep(60)

def handle_message(message_text: str, chat_id: int) -> str:
    msg = message_text.strip()

    if not is_authorized(chat_id):
        if msg == BOT_PASSWORD:
            authorize_user(chat_id, msg, BOT_PASSWORD)
            return "✅ Доступ разрешён. Добро пожаловать, Госпожа!"
        return "🔒 Доступ запрещён. Введи пароль."

    if msg.startswith("/"):
        cmd = msg.split()[0].lower()
        if cmd == "/start":
            return start_text()
        if cmd == "/ping":
            return ping_text()
        if cmd == "/status":
            return render_reminders()
        if cmd == "/nextday":
            today_task = get_today_task()
            if today_task:
                set_postponed_task(today_task)
                return f"⏩ Задача «{today_task}» перенесена на завтра."
            return "Сегодня нет задачи для переноса."
        if cmd == "/ideapost":
            return process_with_ai("сгенерируй идею для поста", chat_id)
        if cmd == "/ideacontent":
            return process_with_ai("сгенерируй идею для съёмки контента", chat_id)
        if cmd == "/ideavideo":
            return process_with_ai("сгенерируй идею для кружочка", chat_id)
        if cmd == "/com":
            return help_text()
        return unknown_command_text()

    ai_result = process_with_ai(msg, chat_id)
    if ai_result:
        return ai_result

    return f"{random_loading_phrase()}\n\n{render_reminders()}"

def run():
    global telegram_client
    tg = TelegramClient(TELEGRAM_BOT_TOKEN)
    telegram_client = tg
    offset: Optional[int] = None
    logger.info("🔥 Бот запущен")

    threading.Thread(target=schedule_daily, daemon=True).start()

    while True:
        try:
            data = tg.get_updates(offset=offset)
            if not data.get("ok"):
                time.sleep(2)
                continue
            for item in data.get("result", []):
                offset = item["update_id"] + 1
                message = item.get("message")
                if not message:
                    continue
                chat_id = message.get("chat", {}).get("id")
                tg.set_chat_id(chat_id)
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
