import os
import re
import traceback
import urllib.parse
from datetime import datetime
from typing import Tuple, Optional
from threading import Thread
from pprint import pformat
from socket import socket
import textwrap


class WorkerThread(Thread):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    MIME_TYPES = {
        "html": "text/html; charset=UTF-8",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif"
    }

    def __init__(self, client_socket: socket, address: Tuple[str, int]):
        super().__init__()

        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:

        try:
            request = self.client_socket.recv(4096)

            with open("server_recv.txt", "wb") as f:
                f.write(request)

            method, path, http_version, request_header, request_body = self.parse_http_request(
                request)

            response_body: bytes
            content_type: Optional[str]
            response_line: str

            if path == "/now":
                html = f"""\
                    <html>
                    <body>
                        <h1>Now: {datetime.now()}</h1>
                    </body>
                    </html>
                """
                response_body = textwrap.dedent(html).encode()
                content_type = "text/html; charset=UTF-8"
                response_line = "HTTP/1.1 200 OK\r\n"

            elif path == "/show_request":
                html = f"""\
                    <html>
                    <body>
                        <h1>Request Line:</h1>
                        <p>
                            {method} {path} {http_version}
                        </p>
                        <h1>Headers:</h1>
                        <pre>{pformat(request_header)}</pre>
                        <h1>Body:</h1>
                        <pre>{request_body.decode("utf-8", "ignore")}</pre>
                    </body>
                    </html>
                """

                response_body = textwrap.dedent(html).encode()
                content_type = "text/html; charset=UTF-8"
                response_line = "HTTP/1.1 200 OK\r\n"

            elif path == "/parameters":
                if method == "GET":
                    response_body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
                    content_type = "text/html; charset=UTF-8"
                    response_line = "HTTP/1.1 405 Method Not Allowed\r\n"

                elif method == "POST":
                    post_params = urllib.parse.parse_qs(request_body.decode())
                    html = f"""
                        <html>
                        <body>
                            <h1>Parameters:</h1>
                            <pre>{pformat(post_params)}</pre>
                        </body>
                        </html>
                    """

                    response_body = textwrap.dedent(html).encode()
                    content_type = "text/html; charset=UTF-8"
                    response_line = "HTTP/1.1 200 OK\r\n"

            else:
                try:
                    response_body = self.get_static_file_content(path)
                    content_type = None
                    response_line = "HTTP/1.1 200 OK\r\n"

                except OSError:
                    response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                    content_type = "text/html; charset=UTF-8"
                    response_line = "HTTP/1.1 404 NOT FOUND \r\n"

            response_header = self.build_response_header(
                path, response_body, content_type)
            response = (response_line + response_header +
                        "\r\n").encode() + response_body

            self.client_socket.send(response)

        except Exception:
            print("There was an error while returning response")
            traceback.print_exec()

        finally:
            print("Ending connection to client...")
            self.client_socket.close()

    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, dict, bytes]:
        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(
            b"\r\n\r\n", maxsplit=1)

        method, path, http_version = request_line.decode().split(" ")

        headers = {}
        for header_row in request_header.decode().split("\r\n"):
            key, value = re.split(r": *", header_row, maxsplit=1)
            headers[key] = value

        return method, path, http_version, headers, request_body

    def get_static_file_content(self, path: str) -> bytes:
        relative_path = path.lstrip("/")
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)
        with open(static_file_path, "rb") as f:
            return f.read()

    def build_response_header(self, path: str, response_body: bytes, content_type: Optional[str]) -> str:

        if content_type is None:
            if "." in path:
                ext = path.rsplit(".", maxsplit=1)[-1]
            else:
                ext = ""

            content_type = self.MIME_TYPES.get(ext, "application/octet-stream")

        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %b %d %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response_body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {content_type}\r\n"

        return response_header
