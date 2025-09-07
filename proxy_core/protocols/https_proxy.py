import asyncio
from proxy_core.proxy_data_tunnel import tunnel_data

async def handle_https(reader, writer, vps_profile, client_ip, initial_data=b""):
    try:
        headers = initial_data
        while b"\r\n\r\n" not in headers:
            chunk = await reader.read(4096)
            if not chunk:
                raise Exception("Нет данных от клиента")
            headers += chunk

        print(f"[DEBUG] Raw Data: {headers[:128]!r}")

        header_lines = headers.decode(errors='ignore').split("\r\n")
        connect_line = header_lines[0]

        if not connect_line.upper().startswith("CONNECT"):
            raise Exception("Некорректный CONNECT-запрос")

        _, host_port, _ = connect_line.split()
        host, port = host_port.split(":")
        port = int(port)

        writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
        await writer.drain()

        await tunnel_data(reader, writer, vps_profile, host, port)
        print(f"[HTTPS] Туннель через {vps_profile['name']} → {host}:{port} от {client_ip}")

    except Exception as e:
        print(f"[HTTPS] Ошибка: {e}")
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass