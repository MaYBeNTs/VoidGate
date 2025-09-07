import json
import os

def load_auht_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    try:
        with open(config_path, "r") as file:
            config = json.load(file)
            return config.get("auth", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
AUTH_CONFIG = load_auht_config()


def authenticate(client_address, crendentials):
    """
    Заглушка аунтификации.

    :param client_address: (str, int) IP-адрес и порт клиента
    :param crendentials: dict c ключами 'username' и 'password'
    :return: True (если доступ разрешен), False - если запрещен
    """

    if not crendentials:
        return False
    
    username = crendentials.get("username")
    password = crendentials.get("password")

    expected_user = AUTH_CONFIG.get("username")
    expected_pass = AUTH_CONFIG.get("password")

    return username == expected_user and password == expected_pass