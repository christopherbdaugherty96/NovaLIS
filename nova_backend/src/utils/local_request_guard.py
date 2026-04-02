from __future__ import annotations

from urllib.parse import urlparse

from fastapi import HTTPException, Request, WebSocket

_ALLOWED_LOOPBACK_HOSTS = {
    "localhost",
    "127.0.0.1",
    "::1",
    "testserver",
}
_LOCAL_ONLY_API_PREFIXES = (
    "/api/memory",
    "/api/settings",
    "/api/workspace",
    "/api/openclaw/agent",
)


def _normalize_host(raw: str | None) -> str:
    text = str(raw or "").strip().split(",", 1)[0].strip().lower()
    if not text:
        return ""
    if text.startswith("["):
        closing = text.find("]")
        if closing != -1:
            text = text[1:closing]
    elif ":" in text:
        text = text.split(":", 1)[0].strip()
    return text


def _origin_host(raw: str | None) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    if text.lower() == "null":
        return "null"
    try:
        parsed = urlparse(text)
    except Exception:
        return ""
    return str(parsed.hostname or "").strip().lower()


def _is_allowed_loopback_host(host: str) -> bool:
    normalized = _normalize_host(host)
    if not normalized:
        return False
    return normalized in _ALLOWED_LOOPBACK_HOSTS or normalized.endswith(".localhost")


def is_local_only_http_path(path: str) -> bool:
    clean = str(path or "").strip()
    return clean.startswith(_LOCAL_ONLY_API_PREFIXES)


def describe_request_rebinding_violation(host: str | None, origin: str | None) -> str | None:
    if not _is_allowed_loopback_host(host):
        return "Local Nova API access requires a loopback Host header."
    origin_host = _origin_host(origin)
    if origin_host and not _is_allowed_loopback_host(origin_host):
        return "Local Nova API access requires a loopback Origin."
    return None


def describe_http_rebinding_violation(request: Request) -> str | None:
    if not is_local_only_http_path(request.url.path):
        return None
    return describe_request_rebinding_violation(
        request.headers.get("host"),
        request.headers.get("origin"),
    )


def require_local_http_request(request: Request) -> None:
    violation = describe_http_rebinding_violation(request)
    if violation:
        raise HTTPException(status_code=403, detail=violation)


def describe_websocket_rebinding_violation(ws: WebSocket) -> str | None:
    headers = getattr(ws, "headers", {}) or {}
    return describe_request_rebinding_violation(
        headers.get("host"),
        headers.get("origin"),
    )
