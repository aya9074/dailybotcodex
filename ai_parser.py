# ai_parser.py - Python версия с DeepSeek (основной) и Groq (резерв)
import os
import json
import random
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from openai import OpenAI  # для DeepSeek
from groq import Groq  # для резерва

# ========== ИНИЦИАЛИЗАЦИЯ ПРОВАЙДЕРОВ ==========
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not DEEPSEEK_API_KEY and not GROQ_API_KEY:
    raise RuntimeError("Нужен хотя бы один API ключ: DEEPSEEK_API_KEY или GROQ_API_KEY")

# Основной клиент (DeepSeek)
deepseek_client = None
if DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )

# Резервный клиент (Groq)
groq_client = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)

# ========== ФУНКЦИЯ ВЫЗОВА ЛЮБОГО ИИ (с переключением) ==========
def call_ai(system_prompt: str, user_prompt: str, max_tokens: int = 150, temperature: float = 0.85) -> Optional[str]:
    """Пытается вызвать DeepSeek, если не выходит — Groq. Возвращает ответ или None."""
    
    # Сначала пробуем DeepSeek (основной)
    if deepseek_client:
        try:
            response = deepseek_client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ DeepSeek упал: {e}. Переключаюсь на Groq.")
    
    # Резерв — Groq
    if groq_client:
        try:
            response = groq_client.chat.completions.create(
                model=os.environ.get("GROQ_MODEL", "llama-3.1-70b-versatile"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Groq тоже упал: {e}")
    
    return None

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
    cookie["preferences"] = [p for p in cookie["preferences"] if datetime.fromisoformat(p["timestamp"]) > cutoff]
    save_cookie(cookie)
    return f"🗑️ Удалила {old_count - len(cookie['facts'])} старых записей"

# ========== ЖЁСТКАЯ ПОДДЕРЖКА ==========
TOUGH_LOVE_PHRASES = [
    "СЛУШАЙ СЮДА. Ты хочешь сделать — делай. Не хочешь — делай через силу. Всё.",
    "Отмазки оставь при себе. Сядь и сделай. Через 10 минут меня не будет, а задача останется.",
    "Ноюни не принимаются. Делай сейчас, потом поплачешь над результатом.",
    "Хватит думать. Открой ноутбук и напиши хоть строчку. Я здесь, но делаешь это ты.",
]

def get_tough_love_response(user_message: str, context: str = "") -> str:
    cookie = load_cookie()
    user_facts = "\n".join([f["text"] for f in cookie["facts"][-5:]]) if cookie["facts"] else "Нет сохранённых фактов"
    
    system_prompt = f"""Ты — жёсткий, но заботливый друг-коуч. Заёбывай пользователя, чтобы он делал дела.
    
О пользователе: {user_facts}

Правила:
- Можно и нужно использовать грубые слова (блять, заебало, твою мать)
- Пиши коротко, 1-2 предложения
- ВСЕГДА заканчивай конкретным призывом к действию
- Используй ЗАГЛАВНЫЕ буквы для удара"""

    user_prompt = f"Пользователь: {user_message}\nКонтекст: {context}\nОтветь коротко и жёстко."

    response = call_ai(system_prompt, user_prompt, max_tokens=150, temperature=0.85)
    if response:
        return response
    return random.choice(TOUGH_LOVE_PHRASES)

# ========== ОТЛОЖЕННЫЕ СООБЩЕНИЯ ==========
SCHEDULED_FILE = "scheduled_messages.json"

def save_scheduled(chat_id: int, text: str, delay_minutes: int) -> str:
    scheduled = []
    if os.path.exists(SCHEDULED_FILE):
        with open(SCHEDULED_FILE, "r") as f:
            scheduled = json.load(f)
    
    send_at = (datetime.now() + timedelta(minutes=delay_minutes)).isoformat()
    scheduled.append({
        "chat_id": chat_id,
        "text": text,
        "send_at": send_at
    })
    
    with open(SCHEDULED_FILE, "w") as f:
        json.dump(scheduled, f, indent=2)
    
    return f"⏰ НАПОМНЮ ЧЕРЕЗ {delay_minutes} МИНУТ. А ТЫ ПОКА РАБОТАЙ."

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

# ========== ЗАГЛУШКА КАЛЕНДАРЯ ==========
def sync_with_calendar(chat_id: int) -> str:
    return "📅 КАЛЕНДАРЬ ЕЩЁ ДЕЛАЮ. НО 'НАПОМНИ ЧЕРЕЗ X МИНУТ' УЖЕ РАБОТАЕТ, БЕЗ ОТМАЗОК."

# ========== ГЛАВНАЯ ФУНКЦИЯ ==========
def process_with_ai(user_message: str, chat_id: int) -> str:
    msg_lower = user_message.lower()
    
    if msg_lower.startswith("обучись") or msg_lower.startswith("запомни"):
        text_to_learn = re.sub(r"^(обучись|запомни)\s*", "", user_message).strip().strip('"')
        if text_to_learn:
            return learn_from_text(text_to_learn)
        return "📝 Напиши после 'обучись:' текст, который я должна запомнить"
    
    if "напомни через" in msg_lower and "минут" in msg_lower:
        match = re.search(r'через\s+(\d+)\s+минут', msg_lower)
        if match:
            minutes = int(match.group(1))
            remaining = user_message[match.end():].strip()
            if remaining:
                return save_scheduled(chat_id, remaining, minutes)
            return save_scheduled(chat_id, "Ты просил напомнить (без текста)", minutes)
    
    if "забудь старое" in msg_lower or "очисти память" in msg_lower:
        return forget_old_info()
    
    if "календарь" in msg_lower:
        return sync_with_calendar(chat_id)
    
    return get_tough_love_response(user_message)
