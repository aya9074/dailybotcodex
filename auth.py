import json
import os

AUTH_FILE = "authorized_users.json"

def load_users():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(AUTH_FILE, "w") as f:
        json.dump(users, f)

def is_authorized(chat_id: int) -> bool:
    users = load_users()
    return str(chat_id) in users

def authorize_user(chat_id: int, entered_password: str, correct_password: str) -> bool:
    if entered_password == correct_password:
        users = load_users()
        users[str(chat_id)] = True
        save_users(users)
        return True
    return False
