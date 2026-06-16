from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src import brain_server
from src.utils.local_request_guard import is_local_only_http_path
from src.utils.route_protection import (
    LOCAL_ONLY_ROUTE_PROTECTIONS,
    PUBLIC_ROUTE_PREFIXES,
    REMOTE_TOKEN_GATED_ROUTE_PREFIXES,
)


SENSITIVE_LOCAL_ROUTES = (
    ("GET", "/api/profile", {}),
    ("POST", "/api/profile/identity", {"json": {"name": "BlockedName"}}),
    ("POST", "/api/profile/preferences", {"json": {"response_style": "concise"}}),
    ("POST", "/api/profile/rules", {"json": {"rules": "blocked"}}),
    ("GET", "/api/token/budget", {}),
    ("GET", "/api/openclaw/bridge/status", {}),
    ("POST", "/api/openclaw/approve-action", {"json": {"run_id": "r1", "tool_name": "noop"}}),
    ("GET", "/phase-status", {}),
    ("GET", "/system/audit/runtime-truth", {}),
    ("GET", "/system/audit/runtime-truth.md", {}),
)


@pytest.mark.parametrize(("method", "path", "kwargs"), SENSITIVE_LOCAL_ROUTES)
def test_sensitive_local_routes_reject_non_loopback_host(method: str, path: str, kwargs: dict):
    client = TestClient(brain_server.app)
    response = client.request(
        method,
        path,
        headers={"Host": "evil.example", "Origin": "https://evil.example"},
        **kwargs,
    )

    assert response.status_code == 403
    assert "loopback" in response.json()["detail"].lower()


def test_media_upload_routes_are_local_only_by_policy():
    assert is_local_only_http_path("/api/live-screen/analyze")
    assert is_local_only_http_path("/stt/transcribe")


def test_remote_bridge_message_is_token_gated_not_local_only():
    assert not is_local_only_http_path("/api/openclaw/bridge/message")

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/bridge/message",
        headers={"Host": "evil.example", "Origin": "https://evil.example"},
        json={"text": "daily brief"},
    )

    assert response.status_code in {401, 503}
    assert response.status_code != 403


def test_every_registered_runtime_route_has_explicit_protection_classification():
    local_prefixes = tuple(item.prefix for item in LOCAL_ONLY_ROUTE_PROTECTIONS)
    offenders: list[str] = []

    for route in brain_server.app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", None)
        if not path or not methods:
            continue
        if path in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
            continue
        text = str(path)
        public = text == "/" or text.startswith(("/landing", "/static"))
        classified = (
            text.startswith(local_prefixes)
            or text.startswith(REMOTE_TOKEN_GATED_ROUTE_PREFIXES)
            or public
        )
        if not classified:
            offenders.append(str(path))

    assert not offenders, "Routes without protection classification: " + ", ".join(sorted(offenders))
