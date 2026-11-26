"""Opt-in dashboard regression.

Install with `python -m pip install -e ".[dev,browser-test]"`
and `python -m playwright install chromium`.
"""

import json
import mimetypes
from contextlib import suppress
from pathlib import Path
from urllib.parse import urlsplit

import pytest

playwright = pytest.importorskip("playwright.sync_api")

STATIC = Path(__file__).resolve().parents[2] / "static"
ORIGIN = "http://nova-dashboard.test"
SETUP_NOTICE = "Weather is available, but no provider key is configured yet."


def test_startup_weather_setup_renders_without_forecast(tmp_path):
    sent_frames = []
    received_frames = []
    browser_errors = []
    external_requests = []

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

    def dashboard_socket(socket):
        if socket.url != "ws://nova-dashboard.test/ws":
            external_requests.append(socket.url)
            socket.close()
            return

        def respond(raw):
            command = json.loads(raw)
            sent_frames.append(command)
            if command.get("text") == "weather" and command.get("silent_widget_refresh"):
                frame = {
                    "type": "weather",
                    "data": {
                        "status": "not_configured",
                        "connected": False,
                        "summary": SETUP_NOTICE,
                        "setup_hint": "Add WEATHER_API_KEY to enable live weather.",
                        "alerts": [],
                        "forecast": "",
                    },
                }
                if command.get("turn_id"):
                    frame["turn_id"] = command["turn_id"]
                received_frames.append(frame)
                socket.send(json.dumps(frame))

        socket.on_message(respond)

    with playwright.sync_playwright() as driver:
        browser = driver.chromium.launch(headless=True)
        try:
            context = browser.new_context(service_workers="block")
            context.route("**/*", dashboard_http)
            context.route_web_socket("**/*", dashboard_socket)
            page = context.new_page()
            page.on("pageerror", lambda error: browser_errors.append(str(error)))
            try:
                page.goto(ORIGIN)
                widget = page.locator("#weather-widget")
                playwright.expect(widget.locator(".weather-line")).to_have_text(SETUP_NOTICE)
                playwright.expect(widget.locator(".weather-forecast, .weather-alerts, .confidence-badge")).to_have_count(0)
                assert received_frames
                assert not browser_errors
                assert not external_requests
            except (AssertionError, playwright.Error):
                (tmp_path / "dashboard-observations.json").write_text(
                    json.dumps({
                        "sent": sent_frames,
                        "received": received_frames,
                        "errors": browser_errors,
                        "external_requests": external_requests,
                    }, indent=2),
                    encoding="utf-8",
                )
                with suppress(playwright.Error):
                    page.screenshot(path=tmp_path / "dashboard.png", timeout=3000)
                raise
        finally:
            browser.close()
