import asyncio
from proxy_core.proxy_data_tunnel import tunnel_data

async def handle_http(reader, writer, vps_profile, client_ip, initial_data=b""):
    try:
        request = initial_data
        while b"\r\n\r\n" not in request:
            chunk = await reader.read(4096)
            if not chunk:
                raise Exception("Нет данных от клиента")
            request += chunk

        lines = request.decode(errors='ignore').split('\r\n')

        # Парсинг первой строки
        first_line = lines[0]
        url = first_line.split()[1]
        if url.startswith("http://"):
            url = url[7:]
        host_port, *_ = url.split("/", 1)
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host = host_port
            port = 80

        await tunnel_data(reader, writer, vps_profile, host, port)
        print(f"[HTTP] Прокси через {vps_profile['name']}: {client_ip} → {host}:{port}")

    except Exception as e:
        print(f"[HTTP] Ошибка: {e}")
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass