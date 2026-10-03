from __future__ import annotations

import ipaddress


def is_loopback_address(raw: str | None) -> bool:
    """Return True only for a literal loopback IP address."""
    try:
        return ipaddress.ip_address(str(raw or "").strip()).is_loopback
    except ValueError:
        return False


def require_loopback_bind_host(raw: str | None) -> str:
    """Validate Nova's local-only listener address and return its normalized text."""
    host = str(raw or "").strip()
    if not is_loopback_address(host):
        raise RuntimeError(
            "NOVA_HOST must be a literal loopback IP address (for example 127.0.0.1 or ::1)."
        )
    return host
