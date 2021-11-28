import os
import traceback
from datetime import datetime
from typing import Tuple
from threading import Thread
from socket import socket


class WorkerThread(Thread):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    MIME_TYPES = {
        "html": "text/html",
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

            try:
                response_body = self.get_static_file_content(path)
                response_line = "HTTP/1.1 200 OK\r\n"

            except OSError:
                response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                response_line = "HTTP/1.1 404 NOT FOUND \r\n"

            response_header = self.build_response_header(path, response_body)
            response = (response_line + response_header +
                        "\r\n").encode() + response_body

            self.client_socket.send(response)

        except Exception:
            print("There was an error while returning response")
            traceback.print_exec()

        finally:
            print("Ending connection to client...")
            self.client_socket.close()

    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, bytes, bytes]:
        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(
            b"\r\n\r\n", maxsplit=1)

        method, path, http_version = request_line.decode().split(" ")

        return method, path, http_version, request_header, request_body

    def get_static_file_content(self, path: str) -> bytes:
        relative_path = path.lstrip("/")
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)
        with open(static_file_path, "rb") as f:
            return f.read()

    def build_response_header(self, path: str, response_body: bytes) -> str:
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
