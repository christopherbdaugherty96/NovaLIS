"""Opt-in dashboard regression.

Install with `python -m pip install -e ".[dev,browser-test]"`
and `python -m playwright install chromium`.
"""

import json
from contextlib import suppress

import pytest
from tests.browser.dashboard_routes import ORIGIN, install_dashboard_routes

playwright = pytest.importorskip("playwright.sync_api")

SETUP_NOTICE = "Weather is available, but no provider key is configured yet."


def test_startup_weather_setup_renders_without_forecast(tmp_path):
    sent_frames = []
    received_frames = []
    browser_errors = []
    console_errors = []
    external_requests = []

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

    def record_console(message):
        if message.type == "error":
            console_errors.append(message.text)

    with playwright.sync_playwright() as driver:
        browser = driver.chromium.launch(headless=True)
        try:
            context = browser.new_context(service_workers="block")
            install_dashboard_routes(context, external_requests)
            context.route_web_socket("**/*", dashboard_socket)
            page = context.new_page()
            page.on("pageerror", lambda error: browser_errors.append(str(error)))
            page.on("console", record_console)
            try:
                page.goto(ORIGIN)
                widget = page.locator("#weather-widget")
                playwright.expect(widget.locator(".weather-line")).to_have_text(SETUP_NOTICE)
                playwright.expect(widget.locator(".weather-forecast, .weather-alerts, .confidence-badge")).to_have_count(0)
                assert received_frames
                assert not browser_errors
                assert not console_errors
                assert not external_requests
            except (AssertionError, playwright.Error):
                (tmp_path / "dashboard-observations.json").write_text(
                    json.dumps({
                        "sent": sent_frames,
                        "received": received_frames,
                        "errors": browser_errors,
                        "console_errors": console_errors,
                        "external_requests": external_requests,
                    }, indent=2),
                    encoding="utf-8",
                )
                with suppress(playwright.Error):
                    page.screenshot(path=tmp_path / "dashboard.png", timeout=3000)
                raise
        finally:
            browser.close()


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
