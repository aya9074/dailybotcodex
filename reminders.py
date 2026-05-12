from typing import Dict, List, Tuple

from storage import load_reminders, save_reminders

def add_reminder(text):
    data = load_reminders()

    if data:
        new_id = str(int(max(data.keys())) + 1)
    else:
        new_id = "1"
Reminder = Tuple[int, str]


def _next_id(data: Dict[str, str]) -> int:
    if not data:
        return 1

    return max(int(key) for key in data.keys()) + 1


def add_reminder(text: str) -> int:
    payload = load_reminders()
    reminder_id = _next_id(payload)
    payload[str(reminder_id)] = text.strip()
    save_reminders(payload)
    return reminder_id


def delete_reminder(reminder_id: int) -> bool:
    payload = load_reminders()
    key = str(reminder_id)

    if key not in payload:
        return False

    data[new_id] = text
    save_reminders(data)
    del payload[key]
    save_reminders(payload)
    return True

    return new_id

def delete_reminder(reminder_id):
    data = load_reminders()
def list_reminders() -> List[Reminder]:
    payload = load_reminders()
    ordered = sorted(payload.items(), key=lambda x: int(x[0]))
    return [(int(reminder_id), text) for reminder_id, text in ordered]

    if reminder_id in data:
        del data[reminder_id]
        save_reminders(data)
        return True

    return False
def render_reminders() -> str:
    reminders = list_reminders()
    if not reminders:
        return "📌 Активных напоминаний нет"

def list_reminders():
    return load_reminders()
    lines = ["📌 Активные напоминания:"]
    lines.extend([f"{rid}. {text}" for rid, text in reminders])
    return "\n".join(lines)
