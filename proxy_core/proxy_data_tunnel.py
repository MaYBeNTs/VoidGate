import asyncio
import socket
import struct

async def tunnel_data(reader1, writer1, vps_profile, target_host, target_port):
    try:
        reader2, writer2 = await asyncio.open_connection(
            vps_profile["vps_host"], int(vps_profile["vps_port"])
        )
        proxy_type = vps_profile["type"].upper()

        if proxy_type == "HTTP":
            connect_str = (
                f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
                f"Host: {target_host}:{target_port}\r\n"
                f"User-Agent: VoidGate/1.0\r\n"
                f"Proxy-Connection: Keep-Alive\r\n\r\n"
            )
            writer2.write(connect_str.encode())
            await writer2.drain()

            resp = await reader2.read(4096)
            if b"200" not in resp.split(b"\r\n")[0]:
                raise Exception(f"HTTP CONNECT не прошел: {resp.decode(errors='ignore')}")

            print(f"[TUNNEL] HTTP прокси подключен: {target_host}:{target_port}")

        else:
            raise Exception("Пока поддерживается только HTTP")

        async def forward(reader, writer):
            try:
                while not reader.at_eof():
                    data = await reader.read(4096)
                    if not data:
                        break
                    writer.write(data)
                    await writer.drain()
            except Exception as e:
                print(f"[TUNNEL] Ошибка в forward: {e}")
            finally:
                try:
                    writer.close()
                    await writer.wait_closed()
                except:
                    pass

        await asyncio.gather(
            forward(reader1, writer2),
            forward(reader2, writer1)
        )

    except Exception as e:
        print(f"[TUNNEL] Ошибка: {e}")
        try:
            writer1.close()
            await writer1.wait_closed()
        except:
            pass