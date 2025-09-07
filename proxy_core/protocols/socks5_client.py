import asyncio
import struct
import socket
from proxy_core.auth_manager import is_valid_credentials, add_credentials_if_needed
from proxy_core.proxy_data_tunnel import tunnel_data

async def handle_socks5(reader, writer, vps_profile, client_ip):
    try:
        client_address = writer.get_extra_info('peername')

        # 1. Метод аутентификации
        ver_nmethods = await reader.readexactly(2)
        version, n_methods = ver_nmethods[0], ver_nmethods[1]
        if version != 0x05:
            raise Exception(f"Неверная версия SOCKS: {version}")
        
        methods = await reader.readexactly(n_methods)

        if 0x02 in methods:
            writer.write(b"\x05\x02")  # username/password
            await writer.drain()

            # Аутентификация
            version = await reader.readexactly(1)
            if version != b"\x01":
                raise Exception("Неверная версия аутентификации")

            ulen = (await reader.readexactly(1))[0]
            username = (await reader.readexactly(ulen)).decode()

            plen = (await reader.readexactly(1))[0]
            password = (await reader.readexactly(plen)).decode()

            if not is_valid_credentials(username, password):
                writer.write(b"\x01\x01")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            add_credentials_if_needed(username, password)
            writer.write(b"\x01\x00")
            await writer.drain()

        elif 0x00 in methods:
            writer.write(b"\x05\x00")  # no auth
            await writer.drain()
        else:
            writer.write(b"\x05\xFF")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        # 2. CONNECT-запрос
        header = await reader.readexactly(4)
        cmd = header[1]
        addr_type = header[3]
        if cmd != 1:
            raise Exception("Только CONNECT поддерживается")

        if addr_type == 1:  # IPv4
            addr = socket.inet_ntoa(await reader.readexactly(4))
        elif addr_type == 3:  # domain
            domain_len = (await reader.readexactly(1))[0]
            addr = (await reader.readexactly(domain_len)).decode()
        else:
            raise Exception(f"Неподдерживаемый тип адреса: {addr_type}")

        port = struct.unpack(">H", await reader.readexactly(2))[0]

        # Ответ клиенту: соединение установлено
        writer.write(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")
        await writer.drain()

        await tunnel_data(reader, writer, vps_profile, addr, port)
        print(f"[SOCKS5] Туннель через {vps_profile['name']}: {client_ip} → {addr}:{port}")

    except Exception as e:
        print(f"[SOCKS5] Ошибка: {e}")
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass