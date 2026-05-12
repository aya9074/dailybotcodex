import random

EMOJI = {
    "ok": "✅",
    "pin": "📌",
    "delete": "🗑",
    "search": "🔎",
    "hello": "👑",
    "thinking": "🤔",
}

LOADING_PHRASES = [
    "ща ща.. я уже работаю",
    "занимаюсь твоей командой",
    "опа! жди, сейчас всё будет",
    "секунду, думаю...",
    "уже кумекаю",
    "ок, момент",
    "принято, обрабатываю",
    "почти готово",
]


def random_loading_phrase() -> str:
    return random.choice(LOADING_PHRASES)


def start_text() -> str:
    return f"бот запущен {EMOJI['hello']}"


def ping_text() -> str:
    return "pong"


def help_text() -> str:
    return (
        "Команды:\n"
        "/start — запуск\n"
        "/ping — проверка\n"
        "/status — список напоминаний\n"
        "\n"
        "Примеры текстом:\n"
        "добавь в напоминания оплатить сервер\n"
        "удали напоминание 2\n"
        "покажи напоминания"
    )


def unknown_command_text() -> str:
    return f"не понял команду {EMOJI['thinking']}"
