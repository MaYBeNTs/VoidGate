# proxy_core/auth_manager.py

import json
import os
from typing import Tuple

AUTH_DB_FILE = "auth_db.json"

# Загружаем базу (если нет — создаём)
def load_auth_db():
    if not os.path.exists(AUTH_DB_FILE):
        with open(AUTH_DB_FILE, 'w') as f:
            json.dump([], f)
    with open(AUTH_DB_FILE, 'r') as f:
        return json.load(f)

# Сохраняем базу
def save_auth_db(db):
    with open(AUTH_DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

# Проверка логина и пароля
def is_valid_credentials(username: str, password: str) -> bool:
    db = load_auth_db()
    return {"username": username, "password": password} in db

# Добавление, если ещё не существует
def add_credentials_if_needed(username: str, password: str):
    db = load_auth_db()
    entry = {"username": username, "password": password}
    if entry not in db:
        db.append(entry)
        save_auth_db(db)

# Только для HTTP Basic Auth
def parse_auth_header(header_value: str) -> Tuple[str, str]:
    import base64
    if not header_value.lower().startswith("basic "):
        return "", ""
    encoded = header_value[6:]
    try:
        decoded = base64.b64decode(encoded).decode("utf-8")
        username, password = decoded.split(":", 1)
        return username, password
    except Exception:
        return "", ""