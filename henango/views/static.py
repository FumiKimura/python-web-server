import os
import traceback

import settings
from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse


def static(request: HTTPRequest) -> HTTPResponse:
    try:
        static_root = getattr(
            settings, "STATIC_ROOT")

        relative_path = request.path.lstrip("/")
        static_file_path = os.path.join(static_root, relative_path)

        with open(static_file_path, "rb") as f:
            response_body = f.read()

        content_type = None
        return HTTPResponse(body=response_body, content_type=content_type, status_code=200)

    except OSError:
        traceback.print_exc()

        response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
        content_type = "text/html"
        response = HTTPResponse(
            body=response_body, content_type=content_type, status_code=404)
