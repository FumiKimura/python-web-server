from typing import Optional


class HTTPResponse:
    status_code: int
    content_type: Optional[str]
    headers: dict
    cookies: dict
    body: bytes

    def __init__(
        self, status_code: int = 200, headers: dict = None, cookies: dict = None, content_type: str = None, body: bytes = b""
    ):
        if headers is None:
            headers = {}

        if cookies is None:
            cookies = {}

        self.status_code = status_code
        self.content_type = content_type
        self.headers = headers
        self.body = body
        self.cookies = cookies
