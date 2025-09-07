import asyncio
from proxy_core.protocol_detector import detect_protocol
from proxy_core.protocols.http_proxy import handle_http
from proxy_core.protocols.https_proxy import handle_https
from proxy_core.protocols.ftp_proxy import handle_ftp
from proxy_core.protocols.socks5_client import handle_socks5

async def handle_connection(reader, writer, vps_profile, client_ip):
    client_addr = writer.get_extra_info("peername")
    try:
        peek = await reader.read(32)
        if not peek:
            writer.close()
            await writer.wait_closed()
            return

        protocol = detect_protocol(peek)

        if protocol == "HTTP":
            await handle_http(reader, writer, vps_profile, client_ip, initial_data=peek)
        elif protocol == "HTTPS":
            await handle_https(reader, writer, vps_profile, client_ip, initial_data=peek)
        elif protocol == "SOCKS5":
            await handle_socks5(reader, writer, vps_profile, client_ip)
        elif protocol == "FTP":
            await handle_ftp(reader, writer, vps_profile, client_ip)
        else:
            print(f"[??] Неизвестный протокол: {client_addr}")
            writer.close()
            await writer.wait_closed()

    except Exception as e:
        print(f"[ERR] Ошибка в соединении: {e}")
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass