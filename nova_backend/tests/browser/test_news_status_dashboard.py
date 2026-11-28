"""Dashboard regression for the governed news availability message."""

import json
from pathlib import Path
from urllib.parse import urlsplit

import pytest

playwright = pytest.importorskip("playwright.sync_api")

STATIC = Path(__file__).resolve().parents[2] / "static"
ORIGIN = "http://nova-dashboard.test"



def test_disabled_news_widget_preserves_backend_status():
    expected = "News is disabled in this runtime profile."

    with playwright.sync_playwright() as driver, driver.chromium.launch(headless=True) as browser:
        context = browser.new_context(service_workers="block")

        def route_asset(route):
            url = urlsplit(route.request.url)
            if f"{url.scheme}://{url.netloc}" != ORIGIN:
                route.abort()
                return
            path = url.path
            if path == "/":
                route.fulfill(path=STATIC / "index.html")
            elif path.startswith("/static/"):
                asset = (STATIC / path.removeprefix("/static/")).resolve()
                if asset.is_relative_to(STATIC) and asset.is_file():
                    route.fulfill(path=asset)
                else:
                    route.abort()
            else:
                route.fulfill(json={})

        def route_socket(socket):
            if socket.url != "ws://nova-dashboard.test/ws":
                socket.close()
                return
            socket.on_message(
                lambda raw: socket.send(json.dumps({
                    "type": "news", "items": [], "categories": {},
                    "status": "disabled", "summary": expected,
                })) if json.loads(raw).get("text") == "news" else None
            )

        context.route("**/*", route_asset)
        context.route_web_socket("**/*", route_socket)
        page = context.new_page()
        page.goto(ORIGIN)
        playwright.expect(page.locator("#news-summary")).to_have_text(expected)
        playwright.expect(page.locator("#news-list li")).to_have_text(expected)
