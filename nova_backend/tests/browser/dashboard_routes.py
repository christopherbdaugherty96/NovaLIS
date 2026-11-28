"""Serve the real dashboard assets without opening an HTTP listener."""

import mimetypes
from pathlib import Path
from urllib.parse import urlsplit

STATIC = Path(__file__).resolve().parents[2] / "static"
ORIGIN = "http://nova-dashboard.test"


def install_dashboard_routes(context, external_requests):
    def dashboard_http(route):
        url = urlsplit(route.request.url)
        if f"{url.scheme}://{url.netloc}" != ORIGIN:
            external_requests.append(route.request.url)
            route.abort()
        elif url.path == "/":
            route.fulfill(path=STATIC / "index.html", content_type="text/html")
        elif url.path.startswith("/static/"):
            asset = (STATIC / url.path.removeprefix("/static/")).resolve()
            if asset.is_relative_to(STATIC) and asset.is_file():
                route.fulfill(path=asset, content_type=mimetypes.guess_type(asset)[0])
            else:
                route.fulfill(status=404)
        else:
            route.fulfill(json={})

    context.route("**/*", dashboard_http)
