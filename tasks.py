import os
import json
import random
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
from groq import Groq
from tasks import get_today_task, get_today_day_name, get_postponed_task, clear_postponed_task

load_dotenv()

# ========== ИНИЦИАЛИЗАЦИЯ GROQ ==========
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY не найден в .env")

groq_client = Groq(api_key=GROQ_API_KEY)

# ========== КОНТЕКСТ И ЦЕЛИ (из твоего JS) ==========
MY_WORK_DESCRIPTION = """
Я — Госпожа, веду Telegram-канал в нише фемдом и финдом. Контент — ноу-нюд.
В постах обычно одна фотография: ножки, каблуки, взгляд сверху вниз, поза доминирования.
В кружочках — короткие фразы: стою, показываю ножки, подмигиваю, говорю что-то властное.
Посты бывают нескольких типов:
- Унижение/доминирование — психологическое давление, напоминание о месте подчинённого
- Финдом — требование денег, трибьюта, подарков
- Привязанность/принадлежность — про зависимость от Госпожи, потребность в контроле
- Посты-зазывалки — короткие, цепляющие, для привлечения новых рабов
"""

MY_GOALS = """
- Публиковать контент по расписанию
- Делать разнообразный контент в рамках фемдом/финдом тематики
- Привлекать новых подписчиков и монетизировать канал
- Удерживать и разогревать аудиторию регулярными постами
- Не повторяться — каждый пост и кружочек должен быть свежим
"""

# ========== ФУНКЦИЯ ВЫЗОВА GROQ ==========
def call_ai(system_prompt: str, user_prompt: str, max_tokens: int = 500, temperature: float = 0.85) -> Optional[str]:
    """Вызывает Groq с перебором моделей"""
    models_to_try = ["llama-3.3-70b-versatile", "llama-3.2-1b-preview", "llama-guard-3-8b"]

    for model_name in models_to_try:
        try:
            response = groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ Groq модель {model_name} упала: {e}")
            continue

    print("❌ Все модели Groq перепробованы, ни одна не работает.")
    return None

# ========== СЕРДЕЧКИ И ЭМОДЗИ ==========
HEARTS = ["🩷", "🤍", "💛", "🧡", "💜", "🩵", "🤎", "💙"]

DAY_EMOJIS = {
    0: "🌸",  # воскресенье
    1: "☕",  # понедельник
    2: "✍️",  # вторник
    3: "🌿",  # среда
    4: "🎬",  # четверг
    5: "💅",  # пятница
    6: "👑",  # суббота
}

# ========== ЕЖЕДНЕВНОЕ СООБЩЕНИЕ (16:00) ==========
def generate_daily_message() -> str:
    """Генерирует полное ежедневное сообщение (мотивация, посты, советы)"""
    day_name = get_today_day_name()
    today_task = get_today_task()
    postponed = get_postponed_task()

    tasks = []
    if postponed:
        tasks.append(postponed)
    if today_task:
        tasks.append(today_task)

    postponed_note = f'Вчера ты перенесла задачу "{postponed}" — сегодня её нужно закрыть.' if postponed else ""

    tasks_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(tasks)]) if tasks else "Сегодня свободный день — можно отдохнуть или сделать что-то для души 🌿"

    system_prompt = f"""Ты — персональный коуч для автора Telegram-канала.
О ней: {MY_WORK_DESCRIPTION.strip()}
Её цели: {MY_GOALS.strip()}

Правила:
- Пиши тепло и по-человечески, как будто знаешь её лично
- Будь конкретным, без воды
- Используй эмодзи уместно, 2-4 штуки на всё сообщение
- Каждый раз формулируй по-новому, не повторяйся"""

    user_prompt = f"""Сегодня {day_name}.
{postponed_note}
Задачи на сегодня: {', '.join(tasks) if tasks else "свободный день"}.

Напиши ТРИ отдельных блока (каждый с новой строки):
1. Наводка для поста — конкретная идея или тема для поста сегодня (1 предложение в кавычках)
2. Наводка для съёмки контента — конкретная идея для видео или кружочка (1 предложение в кавычках)
3. Мотивация — короткая фраза про то, зачем она это делает: ради денег/себя/своего будущего (1-2 предложения)
4. Совет на сегодня — практичный совет по работе с каналом (1-2 предложения)

Формат ответа строго такой (замени содержимое в скобках):
ПОСТ: [идея для поста]
КОНТЕНТ: [идея для съёмки]
МОТИВАЦИЯ: [мотивационная фраза]
СОВЕТ: [практичный совет]"""

    ai_result = call_ai(system_prompt, user_prompt, max_tokens=500, temperature=0.9)

    # Парсим ответ ИИ
    post_idea = "пост про зависимость — они возвращаются снова и снова, потому что ты единственная, кто их принимает такими"
    content_idea = "фото снизу вверх на каблуки, взгляд сверху вниз — классика доминирования, работает всегда"
    motivation = "ты делаешь это ради себя и своего будущего — каждый пост это вложение в свою свободу"
    tip = "не жди идеального настроения — сними кружочек прямо сейчас, живость важнее идеальности"

    if ai_result:
        lines = [line.strip() for line in ai_result.split("\n") if line.strip()]
        for line in lines:
            if line.startswith("ПОСТ:"):
                post_idea = line.replace("ПОСТ:", "").strip()
            elif line.startswith("КОНТЕНТ:"):
                content_idea = line.replace("КОНТЕНТ:", "").strip()
            elif line.startswith("МОТИВАЦИЯ:"):
                motivation = line.replace("МОТИВАЦИЯ:", "").strip()
            elif line.startswith("СОВЕТ:"):
                tip = line.replace("СОВЕТ:", "").strip()

    # Очищаем перенесённую задачу
    clear_postponed_task()

    day_emoji = DAY_EMOJIS.get(datetime.now().weekday() + 1, "🌸")
    heart = random.choice(HEARTS)

    parts = []
    parts.append(f"Привет! Сегодня {day_name} {day_emoji}{', вчера ты перенесла задачу "' + postponed + '"' if postponed else ''}")
    parts.append(f"\n📋 *План на сегодня:*\n{tasks_text}")
    parts.append(f"\n💡 Наводка для поста: \"{post_idea}\"")
    parts.append(f"🎬 Наводка для съёмки контента: \"{content_idea}\"")
    parts.append(f"\n✨ {motivation}")
    parts.append(f"\n📌 Совет на сегодня: {tip}")
    parts.append(f"\nУдачи! {heart}")

    return "\n".join(parts)

# ========== УГЛЫ ДЛЯ ГЕНЕРАЦИИ ИДЕЙ ==========
POST_ANGLES = [
    "унижение через осознание слабости подчинённого",
    "финдом — трибьют, подарок или денежное задание",
    "психологическая привязанность к Госпоже",
    "контроль и принадлежность — ты моя собственность",
    "поклонение ножкам и каблукам",
    "доминирование через уверенность и превосходство",
    "желание заслужить внимание Госпожи",
    "одиночество подчинённого и спасение через служение",
    "игра на чувстве вины и потребности в наказании",
    "зависимость — обычный секс больше не приносит удовольствия",
]

PHOTO_ANGLES = [
    "ножки/каблуки крупным планом с доминирующим ракурсом",
    "взгляд сверху вниз в камеру — холодный и уверенный",
    "поза власти: стоишь, руки на бёдрах, смотришь прямо",
    "каблук на переднем плане, фокус снизу вверх",
    "силуэт со спины — оборачиваешься через плечо",
    "крупно: перчатка, цепочка, поводок или другой атрибут",
    "ноги скрещены, сидишь сверху — взгляд в камеру",
]

VIDEO_ANGLES = [
    "властный взгляд в камеру + короткая фраза-приказ",
    "медленно показываешь ножки/каблуки с уверенной интонацией",
    "холодный взгляд сверху вниз, пауза, усмешка",
    "подмигивание + провокационная фраза про слабость раба",
    "стоишь спиной, медленно оборачиваешься — ни слова",
    "смех Госпожи над ничтожностью подчинённого",
    "короткий приказ с прямым взглядом в камеру",
]

def generate_post_idea() -> str:
    angle = random.choice(POST_ANGLES)
    result = call_ai(
        f"""Ты — ассистент для создания контента в нише фемдом и финдом.
Контекст: {MY_WORK_DESCRIPTION.strip()}
Отвечай коротко. Нужна только идея — не пиши готовый пост.""",
        f"""Придумай одну идею для поста с углом: "{angle}".
Что за крючок? Какую эмоцию или состояние это вызовет у читателя?
Формат: 1-2 предложения — только суть идеи, без готового текста.""",
        max_tokens=150,
        temperature=0.9
    )
    return result or "Пост про момент, когда раб понимает, что уже не может уйти — зависимость сильнее воли. Напомни, что это нормально и ты это принимаешь."

def generate_content_idea() -> str:
    angle = random.choice(PHOTO_ANGLES)
    result = call_ai(
        f"""Ты — ассистент для ноу-нюд фемдом фото-контента в Telegram.
Контекст: {MY_WORK_DESCRIPTION.strip()}
Нужна только идея для фото — поза, детали, ракурс.""",
        f"""Придумай идею для одной фотографии с углом: "{angle}".
Поза, ракурс, детали кадра. Как это визуально передаёт доминирование?
Формат: 1-2 предложения — только идея кадра, без текста поста.""",
        max_tokens=150,
        temperature=0.9
    )
    return result or "Фото снизу вверх: ноги в каблуках на переднем плане, взгляд сверху вниз в камеру — холодный и уверенный. Зритель автоматически чувствует себя внизу."

def generate_video_idea() -> str:
    angle = random.choice(VIDEO_ANGLES)
    result = call_ai(
        f"""Ты — ассистент для видео-кружочков в Telegram (до 60 сек) в нише фемдом.
Контекст: {MY_WORK_DESCRIPTION.strip()}
Кружочки — живые, без монтажа. Нужна только идея.""",
        f"""Придумай идею для кружочка с углом: "{angle}".
Что происходит в кадре? С чего начать, что сделать или сказать?
Формат: 1-2 предложения — только идея, без готового сценария.""",
        max_tokens=150,
        temperature=0.9
    )
    return result or "Стоишь, медленно смотришь в камеру снизу вверх — и говоришь одну фразу про то, что раб уже давно твой, просто ещё не признался себе. Никакого монтажа, только взгляд и голос."

# ========== ЖЁСТКАЯ ПОДДЕРЖКА ==========
TOUGH_LOVE_PHRASES = [
    "СЛУШАЙ СЮДА. Ты хочешь сделать — делай. Не хочешь — делай через силу. Всё.",
    "Отмазки оставь при себе. Сядь и сделай. Через 10 минут меня не будет, а задача останется.",
    "Ноюни не принимаются. Делай сейчас, потом поплачешь над результатом.",
    "Хватит думать. Открой ноутбук и напиши хоть строчку. Я здесь, но делаешь это ты.",
]

def get_tough_love_response(user_message: str, context: str = "") -> str:
    today_task = get_today_task()
    day_name = get_today_day_name()
    task_line = f"Сегодня {day_name}, задача дня: {today_task}" if today_task else f"Сегодня {day_name} — свободный день."

    system_prompt = f"""Ты — жёсткий, но заботливый друг-коуч. Заёбывай пользователя, чтобы он делал дела.
{task_line}

Правила:
- Можно и нужно использовать грубые слова
- Пиши коротко, 1-2 предложения
- ВСЕГДА заканчивай конкретным призывом к действию
- Используй ЗАГЛАВНЫЕ буквы"""

    user_prompt = f"Пользователь: {user_message}\nКонтекст: {context}\nОтветь коротко и жёстко."

    response = call_ai(system_prompt, user_prompt, max_tokens=150, temperature=0.85)
    return response if response else random.choice(TOUGH_LOVE_PHRASES)

# ========== ХРАНИЛИЩЕ ДЛЯ ОБУЧЕНИЯ ==========
LEARNING_COOKIE_FILE = "learning_cookie.json"

def load_cookie() -> Dict[str, Any]:
    if os.path.exists(LEARNING_COOKIE_FILE):
        with open(LEARNING_COOKIE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"facts": [], "preferences": [], "custom_responses": []}

def save_cookie(cookie: Dict[str, Any]):
    with open(LEARNING_COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(cookie, f, ensure_ascii=False, indent=2)

def learn_from_text(text: str) -> str:
    cookie = load_cookie()
    response = call_ai(
        system_prompt="Выдели из текста 1-2 ключевых факта о пользователе. Ответ короткий, 1 предложение максимум.",
        user_prompt=text,
        max_tokens=100,
        temperature=0.7
    )
    if response:
        cookie["facts"].append({"text": response, "timestamp": datetime.now().isoformat()})
        if len(cookie["facts"]) > 50:
            cookie["facts"] = cookie["facts"][-50:]
        save_cookie(cookie)
        return f"✅ Запомнила: {response}"
    return "🤔 Не смогла выделить полезное из этого"

def forget_old_info(days: int = 7) -> str:
    cookie = load_cookie()
    cutoff = datetime.now() - timedelta(days=days)
    old_count = len(cookie["facts"])
    cookie["facts"] = [f for f in cookie["facts"] if datetime.fromisoformat(f["timestamp"]) > cutoff]
    save_cookie(cookie)
    return f"🗑️ Удалила {old_count - len(cookie['facts'])} ст
арых записей"

# ========== ОТЛОЖЕННЫЕ СООБЩЕНИЯ ==========
SCHEDULED_FILE = "scheduled_messages.json"

def save_scheduled(chat_id: int, text: str, delay_minutes: int) -> str:
    scheduled = []
    if os.path.exists(SCHEDULED_FILE):
        with open(SCHEDULED_FILE, "r") as f:
            scheduled = json.load(f)

    send_at = (datetime.now() + timedelta(minutes=delay_minutes)).isoformat()
    scheduled.append({"chat_id": chat_id, "text": text, "send_at": send_at})

    with open(SCHEDULED_FILE, "w") as f:
        json.dump(scheduled, f, indent=2)

    return f"⏰ НАПОМНЮ ЧЕРЕЗ {delay_minutes} МИНУТ."

def get_due_messages() -> List[Dict]:
    if not os.path.exists(SCHEDULED_FILE):
        return []
    with open(SCHEDULED_FILE, "r") as f:
        scheduled = json.load(f)
    now = datetime.now()
    due = [msg for msg in scheduled if datetime.fromisoformat(msg["send_at"]) <= now]
    remaining = [msg for msg in scheduled if datetime.fromisoformat(msg["send_at"]) > now]
    with open(SCHEDULED_FILE, "w") as f:
        json.dump(remaining, f, indent=2)
    return due

def sync_with_calendar(chat_id: int) -> str:
    return "📅 КАЛЕНДАРЬ ЕЩЁ ДЕЛАЮ. НО 'НАПОМНИ ЧЕРЕЗ X МИНУТ' УЖЕ РАБОТАЕТ, БЕЗ ОТМАЗОК."

# ========== ГЛАВНАЯ ФУНКЦИЯ ==========
def process_with_ai(user_message: str, chat_id: int) -> str:
    msg_lower = user_message.lower()

    # План на день
    if any(phrase in msg_lower for phrase in ["план на день", "что делать", "мои задачи", "сегодня что"]):
        today_task = get_today_task()
        day_name = get_today_day_name()
        if today_task:
            return f"📋 *План на {day_name}*:\n🎯 {today_task}\n\nА ТЕПЕРЬ ДЕЛАЙ, НЕ ОТВЛЕКАЙСЯ."
        return f"📋 *{day_name.capitalize()}* — выходной! Отдыхай, но без совсем распиздяйства."

    # Генерация идей
    if "идея для поста" in msg_lower:
        return f"💡 *Идея для поста:*\n{generate_post_idea()}"
    if "идея для съёмки" in msg_lower or "идея контента" in msg_lower:
        return f"📸 *Идея для контента:*\n{generate_content_idea()}"
    if "идея для кружочка" in msg_lower or "идея видео" in msg_lower:
        return f"🎬 *Идея для кружочка:*\n{generate_video_idea()}"

    # Обучение
    if msg_lower.startswith("обучись") or msg_lower.startswith("запомни"):
        text_to_learn = re.sub(r"^(обучись|запомни)\s*", "", user_message).strip().strip('"')
        if text_to_learn:
            return learn_from_text(text_to_learn)
        return "📝 Напиши после 'обучись:' текст, который я должна запомнить"

    # Отложенные сообщения
    if "напомни через" in msg_lower and "минут" in msg_lower:
        match = re.search(r'через\s+(\d+)\s+минут', msg_lower)
        if match:
            minutes = int(match.group(1))
            remaining = user_message[match.end():].strip()
            if remaining:
                return save_scheduled(chat_id, remaining, minutes)
            return save_scheduled(chat_id, "Ты просил напомнить (без текста)", minutes)

    # Очистка памяти
    if "забудь старое" in msg_lower or "очисти память" in msg_lower:
        return forget_old_info()

    # Календарь
    if "календарь" in msg_lower:
        return sync_with_calendar(chat_id)

    # Жёсткая поддержка по умолчанию
    return get_tough_love_response(user_message)
