import textwrap
import urllib.parse
from datetime import datetime
from templates.renderer import render
from pprint import pformat
from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse


def now(request: HTTPRequest) -> HTTPResponse:

    context = {"now": datetime.now()}
    body = render("now.html", context)
    content_type = "text/html; charset=UTF-8"

    return HTTPResponse(body=body)


def show_request(request: HTTPRequest) -> HTTPResponse:
    context = {"request": request, "headers": pformat(
        request.headers), "body": request.body.decode("utf-8", "ignore")}
    body = render("show_request.html", context)

    return HTTPResponse(body=body)


def parameters(request: HTTPRequest) -> HTTPResponse:

    if request.method == "GET":
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"

        return HTTPResponse(body=body, status_code=405)

    elif request.method == "POST":
        context = {"params": urllib.parse.parse_qs(request.body.decode())}
        body = render("parameters.html", context)

        return HTTPResponse(body=body)


def user_profile(request: HTTPRequest) -> HTTPResponse:
    context = {"user_id": request.params["user_id"]}

    body = render("user_profile.html", context)

    return HTTPResponse(body=body)
