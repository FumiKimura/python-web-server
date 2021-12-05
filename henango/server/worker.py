from henango.urls.resolver import URLResolver
import os
import re
import traceback
from urls import url_patterns
from datetime import datetime
from socket import socket
from threading import Thread
from typing import Tuple
from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse
import settings
from urls import url_patterns


class Worker(Thread):

    MIME_TYPES = {
        "html": "text/html; charset=UTF-8",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif"
    }

    STATUS_LINES = {
        200: "200 OK",
        404: "404 Not Found",
        405: "405 Method Not Allowed"
    }

    def __init__(self, client_socket: socket, address: Tuple[str, int]):
        super().__init__()

        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:

        try:
            request_bytes = self.client_socket.recv(4096)

            with open("server_recv.txt", "wb") as f:
                f.write(request_bytes)

            request = self.parse_http_request(request_bytes)

            view = URLResolver().resolve(request)

            response = view(request)

            response_line = self.build_response_line(response)

            response_header = self.build_response_header(response, request)

            response_bytes = (response_line + response_header +
                              "\r\n").encode() + response.body

            self.client_socket.send(response_bytes)

        except Exception:
            print("There was an error while returning response")
            traceback.print_exec()

        finally:
            print("Ending connection to client...")
            self.client_socket.close()

    def parse_http_request(self, request: bytes) -> HTTPRequest:
        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(
            b"\r\n\r\n", maxsplit=1)

        method, path, http_version = request_line.decode().split(" ")

        headers = {}
        for header_row in request_header.decode().split("\r\n"):
            key, value = re.split(r": *", header_row, maxsplit=1)
            headers[key] = value

        return HTTPRequest(path=path, method=method, http_version=http_version, headers=headers, body=request_body)

    def build_response_line(self, response: HTTPResponse) -> str:
        status_line = self.STATUS_LINES[response.status_code]
        return f"HTTP/1.1 {status_line}"

    def build_response_header(self, response: HTTPResponse, request: HTTPRequest) -> str:

        if response.content_type is None:
            if "." in request.path:
                ext = request.path.rsplit(".", maxsplit=1)[-1]
            else:
                ext = ""

            response.content_type = self.MIME_TYPES.get(
                ext, "application/octet-stream")

        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %b %d %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response.body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {response.content_type}\r\n"

        return response_header
