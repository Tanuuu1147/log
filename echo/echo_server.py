import socket
from http import HTTPStatus
from urllib.parse import urlsplit, parse_qs

HOST = "127.0.0.1"
PORT = 5000
BACKLOG = 5
RECV_BUFSIZE = 65536


def _pick_status(query: str) -> HTTPStatus:
    """Get HTTPStatus from query string like "status=404"; default 200 on any issue."""
    try:
        qs = parse_qs(query or "", keep_blank_values=True)
        raw = qs.get("status", [None])[0]
        if raw is None:
            return HTTPStatus.OK
        code = int(str(raw))
        return HTTPStatus(code)
    except Exception:
        return HTTPStatus.OK


def _parse_request(request_text: str):
    """Return (method, path, version, headers_list)

    headers_list is a list of (name, value) preserving order & case as received.
    """
    lines = request_text.split("\r\n")
    if not lines or " " not in lines[0]:
        return "GET", "/", "HTTP/1.1", []

    request_line = lines[0]
    method, path, version = request_line.split(" ", 2)

    headers_list = []
    for line in lines[1:]:
        if not line:
            break
        if ":" in line:
            name, value = line.split(":", 1)
            headers_list.append((name.strip(), value.strip()))
    return method, path, version, headers_list


def _build_response(addr, method: str, path: str, status: HTTPStatus, headers_list):
    body_lines = [
        f"Request Method: {method}",
        f"Request Source: {addr}",
        f"Response Status: {status.value} {status.phrase}",
    ]
    for name, value in headers_list:
        body_lines.append(f"{name}: {value}")
    body = "\n".join(body_lines).encode("utf-8")

    head_lines = [
        f"HTTP/1.1 {status.value} {status.phrase}",
        "Content-Type: text/plain; charset=utf-8",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "Server: simple-echo-socket",
        "",
        "",
    ]
    return "\r\n".join(head_lines).encode("iso-8859-1") + body


def serve(host: str = HOST, port: int = PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(BACKLOG)
        print(f"Echo server listening on http://{host}:{port}")
        while True:
            conn, addr = srv.accept()
            with conn:
                try:
                    data = b""
                    while b"\r\n\r\n" not in data and len(data) < RECV_BUFSIZE:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data += chunk

                    text = data.decode("iso-8859-1", errors="replace")
                    method, path, _version, headers_list = _parse_request(text)
                    parts = urlsplit(path)
                    status = _pick_status(parts.query)

                    response = _build_response(addr, method, path, status, headers_list)
                    conn.sendall(response)
                except Exception as e:
                    body = f"Internal Server Error\n{e}\n".encode("utf-8")
                    head = (
                        f"HTTP/1.1 500 Internal Server Error\r\n"
                        f"Content-Type: text/plain; charset=utf-8\r\n"
                        f"Content-Length: {len(body)}\r\n"
                        f"Connection: close\r\n\r\n"
                    ).encode("iso-8859-1")
                    try:
                        conn.sendall(head + body)
                    except Exception:
                        pass


if __name__ == "__main__":
    try:
        serve()
    except KeyboardInterrupt:
        print("\nShutting down...")
