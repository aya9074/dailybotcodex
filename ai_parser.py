import os
import json
import random
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from tasks import get_today_task, get_today_day_name, get_postponed_task, clear_postponed_task

load_dotenv()

# ========== ИНИЦИАЛИЗАЦИЯ DEEPSEEK ==========
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError("DEEPSEEK_API_KEY не найден в .env")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# ========== КОНТЕКСТ И ЦЕЛИ ==========
MY_WORK_DESCRIPTION = """
Я — Госпожа, веду Telegram-канал в нише фемдом и финдом. Контент — ноу-нюд.
В постах обычно одна-две фотографии: ножки, каблуки, взгляд сверху вниз, поза доминирования.
В кружочках — короткие фразы: стою, показываю ножки, подмигиваю, говорю что-то властное.
Посты бывают нескольких типов:
- Унижение/доминирование — психологическое давление
- Финдом — требование денег, трибьюта, подарков
- Привязанность/принадлежность — про зависимость от Госпожи
- Посты-зазывалки — короткие, для привлечения новых рабов
"""

MY_GOALS = """
- Публиковать контент по расписанию
- Делать разнообразный контент в рамках фемдом/финдом
- Привлекать подписчиков и монетизировать
- Удерживать и разогревать аудиторию
- Не повторяться — каждый пост и кружочек должен быть свежим
"""

# ========== ВЫЗОВ DEEPSEEK ==========
def call_ai(system_prompt: str, user_prompt: str, max_tokens: int = 500, temperature: float = 0.8) -> Optional[str]:
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ DeepSeek ошибка: {e}")
        return None

# ========== СЕРДЕЧКИ И ЭМОДЗИ ==========
HEARTS = ["🩷", "🤍", "💛", "🧡", "💜", "🩵", "🤎", "💙"]
DAY_EMOJIS = {0: "🌸", 1: "☕", 2: "✍️", 3: "🌿", 4: "🎬", 5: "💅", 6: "👑"}

# ========== ЕЖЕДНЕВНОЕ СООБЩЕНИЕ ==========
def generate_daily_message() -> str:
    day_name = get_today_day_name()
    today_task = get_today_task()
    postponed = get_postponed_task()

    tasks = []
    if postponed:
        tasks.append(postponed)
    if today_task:
        tasks.append(today_task)

    postponed_note = f'Вчера ты перенесла задачу "{postponed}" — сегодня её нужно закрыть.' if postponed else ""
    tasks_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(tasks)]) if tasks else "Сегодня свободный день"

    system_prompt = f"""Ты — персональный коуч автора Telegram-канала.
О ней: {MY_WORK_DESCRIPTION.strip()}
Цели: {MY_GOALS.strip()}

Правила: тепло, конкретно, 2-4 эмодзи, не повторяйся."""

    user_prompt = f"""Сегодня {day_name}. {postponed_note}
Задачи: {', '.join(tasks) if tasks else 'свободный день'}.

Формат ответа строго:
ПОСТ: [идея в кавычках]
КОНТЕНТ: [идея для съёмки в кавычках]
МОТИВАЦИЯ: [фраза]
СОВЕТ: [совет]"""

    ai_result = call_ai(system_prompt, user_prompt, max_tokens=500, temperature=0.9)

    post_idea = "пост про зависимость — они возвращаются снова и снова"
    content_idea = "фото снизу вверх на каблуки, взгляд сверху вниз"
    motivation = "ты делаешь это ради себя"
    tip = "не жди идеального настроения"

    if ai_result:
        for line in ai_result.split("\n"):
            line = line.strip()
            if line.startswith("ПОСТ:"):
                post_idea = line.replace("ПОСТ:", "").strip().strip('"')
            elif line.startswith("КОНТЕНТ:"):
                content_idea = line.replace("КОНТЕНТ:", "").strip().strip('"')
            elif line.startswith("МОТИВАЦИЯ:"):
                motivation = line.replace("МОТИВАЦИЯ:", "").strip()
            elif line.startswith("СОВЕТ:"):
                tip = line.replace("СОВЕТ:", "").strip()

    clear_postponed_task()
    day_emoji = DAY_EMOJIS.get(datetime.now().weekday(), "🌸")
    heart = random.choice(HEARTS)

    parts = [f"Привет! Сегодня {day_name} {day_emoji}"]
    parts.append(f"\n📋 *План:*\n{tasks_text}")
    parts.append(f"\n💡 Пост: \"{post_idea}\"")
    parts.append(f"🎬 Контент: \"{content_idea}\"")
    parts.append(f"\n✨ {motivation}")
    parts.append(f"\n📌 {tip}")
    parts.append(f"\nУдачи! {heart}")
    return "\n".join(parts)

# ========== УГЛЫ ДЛЯ ИДЕЙ ==========
POST_ANGLES = [
    "унижение через слабость подчинённого",
    "финдом — трибьют, подарок",
    "психологическая привязанность",
    "контроль — ты моя собственность",
    "поклонение ножкам и каблукам",
    "доминирование через уверенность",
    "одиночество раба и спасение через служение",
    "зависимость — обычный секс не нужен"
]

PHOTO_ANGLES = [
    "ножки/каблуки крупным планом",
    "взгляд сверху вниз в камеру",
    "поза власти: руки на бёдрах",
    "каблук на переднем плане снизу вверх",
    "силуэт со спины через плечо",
    "атрибуты: перчатка, цепочка",
    "ноги скрещены, сидишь сверху"
]

VIDEO_ANGLES = [
    "властный взгляд + короткий приказ",
    "медленно показываешь ножки/каблуки",
    "холодный взгляд, пауза, усмешка",
    "подмигивание + фраза про слабость раба",
    "стоишь спиной, медленно оборачиваешься",
    "смех Госпожи над ничтожностью",
    "короткий приказ с прямым взглядом"
]

def generate_post_idea() -> str:
    angle = random.choice(POST_ANGLES)
    prompt = f"""Ты — креативный помощник для фемдом/финдом канала.
Контекст: {MY_WORK_DESCRIPTION[:500]}
Цели: {MY_GOALS[:300]}
Угол: {angle}
Придумай развёрнутую, чёткую, готовую к использованию идею для поста (3-5 предложений).
Идея должна быть эмоциональной, провокационной, без левых тем. Без капса."""
    return call_ai(prompt, "Создай идею для поста", max_tokens=300, temperature=0.8) or "Пост про зависимость, когда раб понимает, что уйти не может."

def generate_content_idea() -> str:
    angle = random.choice(PHOTO_ANGLES)
    prompt = f"""Ты — ассистент по визуальному контенту (ноу-нюд фемдом).
Контекст: {MY_WORK_DESCRIPTION[:500]}
Угол: {angle}
Придумай детализированную идею для фотографии: поза, ракурс, освещение, настроение.
2-3 предложения, передать доминирование. Без капса."""
    return call_ai(prompt, "Идея для фото", max_tokens=250, temperature=0.8) or "Фото снизу вверх: ноги в каблуках, взгляд сверху вниз"

def generate_video_idea() -> str:
    angle = random.choice(VIDEO_ANGLES)
    prompt = f"""Ты — режиссёр микророликов для фемдом Telegram (до 60 сек).
Контекст: {MY_WORK_DESCRIPTION[:500]}
Угол: {angle}
Опиши короткую сцену: действие, мимика, фраза. Живо, без монтажа.
2-3 предложения, доминантно, без капса."""
    return call_ai(prompt, "Идея для кружочка", max_tokens=250, temperature=0.8) or "Смотришь в камеру и говоришь: Ты всё сделаешь, потому что я так хочу."
# ========== ПОДДЕРЖКА ==========
TOUGH_PHRASES = [
    "Давай, ты справишься. Делай сейчас, ной потом.",
    "Отмазки в сторону — ты делаешь это ради себя. Работай.",
    "Не хочешь — делай через силу. Ты себе в будущем скажешь спасибо."
]

def get_tough_love_response(msg: str) -> str:
    task = get_today_task()
    day = get_today_day_name()
    line = f"Сегодня {day}, задача: {task}" if task else f"Сегодня {day} — отдых"
    prompt = f"""Ты — жёсткий, но заботливый коуч. Помогай пользователю не бросать дела.
{line}
Правила:
- Можно использовать лёгкие грубые слова
- НЕ пиши ЗАГЛАВНЫМИ БУКВАМИ.Используй ЗАГЛАВНЫЕ БУКВЫ ситуативно, когда нужно поддержать
- ВСЕГДА добавляй в конце напоминание: "ты делаешь это ради себя" или "это ради будущего" или "ради денег"
- Пиши сообщения среднего объема, призывай к действию"""
    resp = call_ai(prompt, f"Ответь пользователю (без капса, с поддержкой): {msg}", max_tokens=150, temperature=0.7)
    if resp:
        return resp
    return random.choice(TOUGH_PHRASES)
# ========== ОБУЧЕНИЕ ==========
COOKIE_FILE = "learning_cookie.json"

def load_cookie() -> dict:
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"facts": []}

def save_cookie(cookie: dict):
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(cookie, f, ensure_ascii=False, indent=2)

def learn_from_text(text: str) -> str:
    cookie = load_cookie()
    resp = call_ai("Выдели 1 факт о пользователе (1 предложение).", text, max_tokens=100, temperature=0.5)
    if resp:
        cookie["facts"].append({"text": resp, "timestamp": datetime.now().isoformat()})
        if len(cookie["facts"]) > 50:
            cookie["facts"] = cookie["facts"][-50:]
        save_cookie(cookie)
        return f"✅ Запомнила: {resp}"
    return "🤔 Не смогла"

def forget_old_info(days: int = 7) -> str:
    cookie = load_cookie()
    cutoff = datetime.now() - timedelta(days=days)
    old = len(cookie["facts"])
    cookie["facts"] = [f for f in cookie["facts"] if datetime.fromisoformat(f["timestamp"]) > cutoff]
    save_cookie(cookie)
    return f"🗑️ Удалила {old - len(cookie['facts'])} записей"

# ========== ОТЛОЖЕННЫЕ ==========
SCHED_FILE = "scheduled_messages.json"

def save_scheduled(chat_id: int, text: str, delay_minutes: int) -> str:
    scheduled = []
    if os.path.exists(SCHED_FILE):
        with open(SCHED_FILE, "r") as f:
            scheduled = json.load(f)
    send_at = (datetime.now() + timedelta(minutes=delay_minutes)).isoformat()
    scheduled.append({"chat_id": chat_id, "text": text, "send_at": send_at})
    with open(SCHED_FILE, "w") as f:
        json.dump(scheduled, f, indent=2)
    return f"⏰ Напомню через {delay_minutes} минут"

def get_due_messages() -> List[Dict]:
    if not os.path.exists(SCHED_FILE):
        return []
    with open(SCHED_FILE, "r") as f:
        scheduled = json.load(f)
    now = datetime.now()
    due = [m for m in scheduled if datetime.fromisoformat(m["send_at"]) <= now]
    remaining = [m for m in scheduled if datetime.fromisoformat(m["send_at"]) > now]
    with open(SCHED_FILE, "w") as f:
        json.dump(remaining, f, indent=2)
    return due

def sync_with_calendar(chat_id: int) -> str:
    return "📅 Календарь в разработке. Используй 'напомни через X минут'."

# ========== ГЛАВНЫЙ ПРОЦЕССОР ==========
def process_with_ai(user_message: str, chat_id: int) -> str:
    msg_lower = user_message.lower()

    # План на день
    if any(x in msg_lower for x in ["план на день", "что делать", "мои задачи", "сегодня что"]):
        task = get_today_task()
        day = get_today_day_name()
        if task:
            return f"📋 *План на {day}:* {task}\n\nА ТЕПЕРЬ ДЕЛАЙ."
        return f"📋 *{day.capitalize()}* — выходной. Отдыхай."

    # Генерация идей
    if "идея для поста" in msg_lower:
        return f"💡 *Идея поста:*\n{generate_post_idea()}"
    if "идея для съёмки" in msg_lower or "идея контента" in msg_lower:
        return f"📸 *Идея контента:*\n{generate_content_idea()}"
    if "идея для кружочка" in msg_lower or "идея видео" in msg_lower:
        return f"🎬 *Идея кружочка:*\n{generate_video_idea()}"

    # Обучение
    if msg_lower.startswith("обучись") or msg_lower.startswith("запомни"):
        text = re.sub(r"^(обучись|запомни)\s*", "", user_message).strip().strip('"')
        if text:
            return learn_from_text(text)
        return "📝 Напиши после 'обучись:' текст"

    # Отложенные
    if "напомни через" in msg_lower and "минут" in msg_lower:
        match = re.search(r'через\s+(\d+)\s+минут', msg_lower)
        if match:
            minutes = int(match.group(1))
            rest = user_message[match.end():].strip()
            return save_scheduled(chat_id, rest or "без текста", minutes)

    # Очистка памяти
    if "забудь старое" in msg_lower or "очисти память" in msg_lower:
        return forget_old_info()

    # Календарь
    if "календарь" in msg_lower:
        return sync_with_calendar(chat_id)

    # Жёсткая поддержка
    return get_tough_love_response(user_message)
root@ubuntu-s-1vcpu-1gb-ams3:~/dailybotcodex#
