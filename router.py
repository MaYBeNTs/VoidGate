import asyncio

from proxy_core.proxy_data_tunnel import tunnel_data

# Универсальный маршрутизатор
async def route_traffic(reader, writer, vps_profile, client_ip):
    try:
        # Лог клиента
        client_address = writer.get_extra_info('peername')
        print(f"[ROUTER] Получено соединение от {client_address}")

        # Подключение к VPS
        vps_host = vps_profile['vps_host']
        vps_port = int(vps_profile['vps_port'])

        await tunnel_data(reader, writer, vps_host, vps_port)

    except Exception as e:
        print(f"[ROUTER] Ошибка маршрутизации: {e}")
        writer.close()
        await writer.wait_closed()