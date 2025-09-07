import os
import socket
import json
import asyncio
from connection_handler import handle_connection

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"profiles": {}, "protocol_ports": {}, "client_ip": "auto"}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_client_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def profile_menu(config):
    while True:
        print("\n|====|VoidGate|====|")
        print("1. Добавить профиль")
        print("2. Изменить профиль")
        print("3. Удалить профиль")
        print("4. Запустить VoidGate")
        choice = input("Выбор: ").strip()

        if choice == "1":
            add_profile(config)
        elif choice == "2":
            edit_profile(config)
        elif choice == "3":
            delete_profile(config)
        elif choice == "4":
            return
        else:
            print("Неверный выбор.")

def add_profile(config):
    proto = input("Протокол: ").lower()
    name = input("Имя профиля: ").strip()
    host = input("VPS IP: ").strip()
    port = input("VPS порт: ").strip()
    login = input("Логин (нажмите Enter если не требуется): ").strip()
    password = input("Пароль (нажмите Enter если не требуется): ").strip()

    config["profiles"][proto] = {
        "type": proto,
        "name": name,
        "vps_host": host,
        "vps_port": port,
        "username": login if login else "",
        "password": password if password else ""
    }

    if proto not in config["protocol_ports"]:
        port_local = input(f"Локальный порт для {proto}: ").strip()
        config["protocol_ports"][proto] = int(port_local)

    save_config(config)
    print("Профиль добавлен.")

def edit_profile(config):
    profiles = config["profiles"]
    if not profiles:
        print("Нет профилей для изменения.")
        return

    print("\nДоступные профили:")
    for i, p in enumerate(profiles.keys(), 1):
        print(f"{i}. {p}")
    choice = input("Выберите профиль: ").strip()

    keys = list(profiles.keys())
    if not choice.isdigit() or not (1 <= int(choice) <= len(keys)):
        print("❌ Неверный выбор.")
        return

    proto = keys[int(choice) - 1]
    profile = profiles[proto]

    print(f"\nИзменение профиля: {proto}")
    for field in ["name", "vps_host", "vps_port", "username", "password"]:
        current = profile.get(field, "")
        new_value = input(f"{field} (текущий: {current}) → ").strip()
        if new_value:
            profile[field] = new_value

    config["profiles"][proto] = profile
    save_config(config)
    print("Профиль обновлён.")

def delete_profile(config):
    profiles = config["profiles"]
    if not profiles:
        print("Нет профилей для удаления.")
        return

    print("\nДоступные профили:")
    for i, p in enumerate(profiles.keys(), 1):
        print(f"{i}. {p}")
    choice = input("Выберите номер профиля: ").strip()

    keys = list(profiles.keys())
    if not choice.isdigit() or not (1 <= int(choice) <= len(keys)):
        print("Неверный выбор!")
        return

    proto = keys[int(choice) - 1]
    del profiles[proto]
    save_config(config)
    print(f"Профиль {proto} удалён!")

async def start_server(protocol, port, handler, vps_profile, client_ip):
    async def wrapper(reader, writer):
        await handler(reader, writer, vps_profile, client_ip)
    server = await asyncio.start_server(wrapper, "0.0.0.0", port)
    print(f"[+] {protocol} сервер запущен на порту {port}")
    return server

async def main():
    config = load_config()
    profile_menu(config)

    client_ip = get_client_ip() if config.get("client_ip") == "auto" else config["client_ip"]
    print(f"[INFO] Локальный IP клиента: {client_ip}\n")

    protocols = list(config["profiles"].keys())
    print("Доступные профили:")
    for i, proto in enumerate(protocols, 1):
        print(f"  {i}. {proto} → {config['profiles'][proto]['name']}")
    choice = input("\nВыберите номер протокола: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(protocols)):
        print("Неверный выбор.")
        return
    proto = protocols[int(choice) - 1]

    profile = config["profiles"][proto]
    port = config["protocol_ports"].get(proto)
    if not profile or not port:
        print(f"[!] Профиль или порт не задан.")
        return

    print(f"\n[*] Запуск VoidGate для протокола: {proto} ({profile['name']})")

    server = await start_server(proto, port, handle_connection, profile, client_ip)
    print("=[*] VoidGate успешно запущен! Ожидание соединений...\n")
    await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Завершение по Ctrl + C")