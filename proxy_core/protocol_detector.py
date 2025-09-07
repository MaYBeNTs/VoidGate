def detect_protocol(peek: bytes) -> str:
    http_methods = [b"GET", b"POST", b"HEAD", b"PUT", b"DELETE", b"OPTIONS", b"PATCH", b"CONNECT"]
    for method in http_methods:
        if peek.startswith(method):
            return "HTTP" if method != b"CONNECT" else "HTTPS"
    if peek.startswith(b"USER") or peek.startswith(b"PASS"):
        return "FTP"
    elif peek.startswith(b"\x05"):
        return "SOCKS5"
    else:
        return "UNKNOWN"