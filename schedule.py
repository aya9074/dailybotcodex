from datetime import datetime
from typing import Dict, Optional

WEEKLY_SCHEDULE: Dict[int, str] = {
    0: "",  # воскресенье — свободный день
    1: "запись контента",  # понедельник
    2: "пост в канал",  # вторник
    3: "",  # среда — свободный день
    4: "кружочек",  # четверг
    5: "пост-зазывалка",  # пятница
    6: "пост-зазывалка",  # суббота
}

DAY_NAMES: Dict[int, str] = {
    0: "воскресенье",
    1: "понедельник",
    2: "вторник",
    3: "среда",
    4: "четверг",
    5: "пятница",
    6: "суббота",
}

_postponed_task: Optional[str] = None


def get_today_task(now: Optional[datetime] = None) -> Optional[str]:
    date = now or datetime.utcnow()
    day = int(date.strftime("%w"))
    task = WEEKLY_SCHEDULE.get(day, "")

    if not task.strip():
        return None

    return task


def get_today_day_name(now: Optional[datetime] = None) -> str:
    date = now or datetime.utcnow()
    day = int(date.strftime("%w"))
    return DAY_NAMES.get(day, "день")


def get_postponed_task() -> Optional[str]:
    return _postponed_task


def set_postponed_task(task: str) -> None:
    global _postponed_task
    _postponed_task = task


def clear_postponed_task() -> None:
    global _postponed_task
    _postponed_task = None
