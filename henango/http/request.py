class HTTPRequest:
    path: str
    method: str
    http_version: str
    headers: dict
    body: bytes
    params: dict
    cookies: dict

    def __init__(
        self, path: str = "", method: str = "", http_version: str = "", headers: dict = None, cookies: dict = None, body: bytes = b"", params: dict = None
    ):
        if headers is None:
            headers = {}

        if params is None:
            params = {}

        if cookies is None:
            cookies = {}

        self.path = path
        self.method = method
        self.http_version = http_version
        self.headers = headers
        self.body = body
        self.params = params
        self.cookies = cookies
