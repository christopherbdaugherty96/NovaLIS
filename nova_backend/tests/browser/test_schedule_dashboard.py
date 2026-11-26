"""Opt-in dashboard conversation regression using Nova's ASGI WebSocket."""

import json
from contextlib import suppress
from datetime import datetime, timezone

import anyio
import pytest
from starlette.testclient import TestClient
from tests.browser.dashboard_routes import ORIGIN, install_dashboard_routes

playwright = pytest.importorskip("playwright.sync_api")

TURNS = (
    "What do I have coming up?",
    "When is the first one?",
    "Tell me more about the second one.",
)


def test_dashboard_preserves_schedule_across_two_followups(monkeypatch, tmp_path):
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(tmp_path / "runtime"))
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")

    from src import brain_server
    from src.brief import daily_loop
    from src.llm import llm_gateway

    attempts = []

    def deny_io(*args, **kwargs):
        attempts.append("provider or inference call")
        raise AssertionError(attempts[-1])

    monkeypatch.setattr("src.governor.network_mediator.NetworkMediator.request", deny_io)
    monkeypatch.setattr("src.llm.model_network_mediator.ModelNetworkMediator.request_json", deny_io)
    monkeypatch.setattr("src.llm.model_network_mediator.ModelNetworkMediator.request_stream", deny_io)
    monkeypatch.setattr("src.skills.general_chat.generate_chat", deny_io)
    monkeypatch.setattr(llm_gateway.llm_manager, "inference_blocked", True)
    monkeypatch.setattr(llm_gateway.llm_manager, "health_check", lambda: False)

    calendar_reads = []
    project = daily_loop.compose_daily_loop_projection

    def with_calendar_fixture(**kwargs):
        calendar_reads.append(True)
        kwargs["session_state"] = {
            **kwargs["session_state"],
            "last_calendar_events": [
                {"title": "Cedar review", "date": "2027-01-14", "time": "2:30 PM"},
                {"title": "Birch check-in", "date": "2027-01-15", "time": "4:00 PM"},
            ],
        }
        kwargs["now"] = datetime(2026, 11, 25, tzinfo=timezone.utc)
        return project(**kwargs)

    monkeypatch.setattr(daily_loop, "compose_daily_loop_projection", with_calendar_fixture)
    browser_frames = []
    backend_frames = []
    errors = []
    external_requests = []

    with (
        TestClient(brain_server.app).websocket_connect("/ws") as backend,
        playwright.sync_playwright() as driver,
        driver.chromium.launch(headless=True) as browser,
    ):
        context = browser.new_context(service_workers="block")
        install_dashboard_routes(context, external_requests)

        def connect(socket):
            if socket.url != "ws://nova-dashboard.test/ws":
                external_requests.append(socket.url)
                socket.close()
                return

            async def receive_through_turn(turn_id):
                with anyio.fail_after(5):
                    while True:
                        message = await backend._send_rx.receive()
                        backend._raise_on_close(message)
                        frame = json.loads(message["text"])
                        if frame.get("turn_id") != turn_id or frame["type"] not in {"chat", "chat_done"}:
                            continue
                        backend_frames.append(frame)
                        socket_messages.append(frame)
                        if frame["type"] == "chat_done":
                            return

            def forward(raw):
                command = json.loads(raw)
                browser_frames.append(command)
                # Keep provider and startup behavior outside this manual-turn regression.
                if command.get("text") not in TURNS:
                    return
                socket_messages.clear()
                backend.send_text(raw)
                backend.portal.call(receive_through_turn, command["turn_id"])
                for frame in socket_messages:
                    socket.send(json.dumps(frame))

            socket_messages = []
            backend.portal.call(receive_through_turn, None)
            for frame in socket_messages:
                socket.send(json.dumps(frame))
            socket.on_message(forward)

        context.route_web_socket("**/*", connect)
        page = context.new_page()
        page.add_init_script("""localStorage.setItem("nova_first_run_done", "1");
            localStorage.setItem("nova_active_page", "chat");""")
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
        displayed = []
        try:
            page.goto(ORIGIN)
            page.set_default_timeout(5000)
            composer = page.locator("#chat-input")
            replies = page.locator("#chat-log .chat-assistant")
            playwright.expect(composer).to_be_visible()
            for prompt in TURNS:
                count = replies.count()
                composer.fill(prompt)
                composer.press("Enter")
                playwright.expect(replies).to_have_count(count + 1)
                if prompt == TURNS[0]:
                    replies.last.get_by_role("button", name="Show more", exact=True).click()
                displayed.append(replies.last.locator(":scope > span").first.inner_text())

            sent = [frame for frame in browser_frames if frame.get("text") in TURNS]
            assert [frame["text"] for frame in sent] == list(TURNS)
            turn_ids = [frame["turn_id"] for frame in sent]
            assert all(turn_ids) and len(set(turn_ids)) == len(TURNS)
            for turn_id, answer in zip(turn_ids, displayed, strict=True):
                correlated = [
                    frame
                    for frame in backend_frames
                    if frame.get("turn_id") == turn_id and frame["type"] in {"chat", "chat_done"}
                ]
                assert [frame["type"] for frame in correlated] == ["chat", "chat_done"]
                assert answer == correlated[0]["message"]
                assert "[source: calendar]" in correlated[0]["message"]

            upcoming, first, second = displayed
            assert upcoming.index("Cedar review") < upcoming.index("Birch check-in")
            assert "2:30 PM" in first and "4:00 PM" not in first
            assert "2:30 PM \u2014 Cedar review" in upcoming
            assert "Birch check-in" in second and "4:00 PM" in second
            assert "Cedar review" not in second
            assert "2027-01-14" in first
            assert "inference is currently locked" in backend_frames[0]["message"]
            assert calendar_reads == [True]
            assert not attempts
            assert not external_requests
            assert not errors
        except Exception:
            (tmp_path / "schedule-browser-observations.json").write_text(
                json.dumps({
                    "displayed": displayed,
                    "browser_frames": browser_frames,
                    "backend_frames": backend_frames,
                    "errors": errors,
                    "external_requests": external_requests,
                    "blocked_calls": attempts,
                }, indent=2),
                encoding="utf-8",
            )
            with suppress(playwright.Error):
                page.screenshot(path=tmp_path / "schedule-dashboard.png", timeout=3000)
            raise
