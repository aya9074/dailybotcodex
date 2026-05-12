# reminders.py
from typing import Dict, List, Tuple
from storage import load_reminders, save_reminders

# Тип для напоминания (id, текст)
Reminder = Tuple[int, str]

def _next_id(data: Dict[str, str]) -> int:
    """Генерирует следующий ID для напоминания"""
    if not data:
        return 1
    return max(int(key) for key in data.keys()) + 1

def add_reminder(text: str) -> int:
    """Добавляет напоминание и возвращает его ID"""
    payload = load_reminders()
    reminder_id = _next_id(payload)
    payload[str(reminder_id)] = text.strip()
    save_reminders(payload)
    return reminder_id

def delete_reminder(reminder_id: int) -> bool:
    """Удаляет напоминание по ID. Возвращает True, если удалилось"""
    payload = load_reminders()
    key = str(reminder_id)
    
    if key not in payload:
        return False
    
    del payload[key]
    save_reminders(payload)
    return True

def list_reminders() -> List[Reminder]:
    """Возвращает список всех напоминаний [(id, текст), ...]"""
    payload = load_reminders()
    ordered = sorted(payload.items(), key=lambda x: int(x[0]))
    return [(int(reminder_id), text) for reminder_id, text in ordered]

def render_reminders() -> str:
    """Возвращает красивое текстовое представление напоминаний для отправки в Telegram"""
    reminders = list_reminders()
    
    if not reminders:
        return "📌 Активных напоминаний нет"
    
    lines = ["📌 *Активные напоминания:*"]
    for rid, text in reminders:
        lines.append(f"{rid}. {text}")
    
    return "\n".join(lines)
