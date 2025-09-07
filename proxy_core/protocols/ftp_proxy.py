import asyncio
from proxy_core.auth_manager import is_valid_credentials, add_credentials_if_needed
from proxy_core.proxy_data_tunnel import tunnel_data

async def handle_ftp(reader1, writer1, client_address, client_ip):
    try:
        writer1.write(b"220 FTP proxy ready\r\n")
        await writer1.drain()

        user_line = (await reader1.readline()).decode().strip()
        if not user_line.lower().startswith("user "):
            writer1.write(b"530 Invalid USER\r\n")
            await writer1.drain()
            writer1.close()
            await writer1.wait_closed()
            return
        username = user_line.split(" ", 1)[1]

        writer1.write(b"331 Password required\r\n")
        await writer1.drain()

        pass_line = (await reader1.readline()).decode().strip()
        if not pass_line.lower().startswith("pass "):
            writer1.write(b"530 Invalid PASS\r\n")
            await writer1.drain()
            writer1.close()
            await writer1.wait_closed()
            return
        password = pass_line.split(" ", 1)[1]

        if not is_valid_credentials(username, password):
            writer1.write(b"530 Login incorrect\r\n")
            await writer1.drain()
            writer1.close()
            await writer1.wait_closed()
            return
        add_credentials_if_needed(username, password)

        writer1.write(b"230 Login successful\r\n")
        await writer1.drain()

        cmd_line = (await reader1.readline()).decode().strip()
        if cmd_line.lower().startswith("open "):
            parts = cmd_line.split()
            if len(parts) == 3:
                host = parts[1]
                port = int(parts[2])
            else:
                writer1.write(b"500 Invalid OPEN command\r\n")
                await writer1.drain()
                writer1.close()
                await writer1.wait_closed()
                return
        else:
            writer1.write(b"500 Expected OPEN command\r\n")
            await writer1.drain()
            writer1.close()
            await writer1.wait_closed()
            return

        reader2, writer2 = await asyncio.open_connection(host, port)
        print(f"[FTP] Прокси: {client_address} -> {host}:{port}")
        await tunnel_data(reader1, writer1, reader2, writer2, client_address)

    except Exception as e:
        print(f"[FTP] Ошибка: {e}")
        writer1.close()
        await writer1.wait_closed()