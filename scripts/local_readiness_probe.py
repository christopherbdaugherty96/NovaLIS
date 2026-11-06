#!/usr/bin/env python3
"""Direct, proxy-free readiness probe for Nova's loopback HTTP endpoint."""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "nova_backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.utils.loopback_bind import require_loopback_bind_host


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(newurl, code, msg, headers, fp)


def _validated_port(value: object) -> int:
    if isinstance(value, bool):
        raise RuntimeError("Nova readiness port must be an integer from 1 to 65535.")
    try:
        port = int(value)
    except (TypeError, ValueError) as error:
        raise RuntimeError(
            "Nova readiness port must be an integer from 1 to 65535."
        ) from error
    if not 1 <= port <= 65535:
        raise RuntimeError("Nova readiness port must be an integer from 1 to 65535.")
    return port


def phase_status_url(host: object, port: object) -> str:
    """Return the one admitted readiness URL without performing I/O."""
    loopback = require_loopback_bind_host(None if host is None else str(host))
    validated_port = _validated_port(port)
    url_host = f"[{loopback}]" if ":" in loopback else loopback
    return f"http://{url_host}:{validated_port}/phase-status"


def probe_phase_status(*, host: object, port: object, timeout: float) -> bool:
    """Probe Nova directly, with proxies and redirects disabled."""
    url = phase_status_url(host, port)
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        _NoRedirectHandler(),
    )
    request = urllib.request.Request(url, method="GET")
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status == 200
    except (OSError, urllib.error.HTTPError, urllib.error.URLError):
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe Nova's loopback readiness endpoint.")
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args(argv)
    try:
        ready = probe_phase_status(host=args.host, port=args.port, timeout=args.timeout)
    except RuntimeError as error:
        print(f"[Nova] ERROR: {error}", file=sys.stderr)
        return 2
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
