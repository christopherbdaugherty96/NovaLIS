from __future__ import annotations

import importlib.util
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROBE_PATH = PROJECT_ROOT / "scripts" / "local_readiness_probe.py"


def _load_probe():
    spec = importlib.util.spec_from_file_location("local_readiness_probe", PROBE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("127.0.0.1", "http://127.0.0.1:8000/phase-status"),
        ("127.0.0.2", "http://127.0.0.2:8123/phase-status"),
        ("::1", "http://[::1]:8000/phase-status"),
    ],
)
def test_readiness_url_accepts_only_literal_loopback(host, expected):
    probe = _load_probe()
    port = 8123 if host == "127.0.0.2" else 8000
    assert probe.phase_status_url(host, port) == expected


@pytest.mark.parametrize(
    "host",
    ["localhost", "0.0.0.0", "192.168.1.20", "example.com", "user@127.0.0.1"],
)
def test_readiness_url_rejects_untrusted_host_before_opener(monkeypatch, host):
    probe = _load_probe()
    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda *_args: pytest.fail("denial must not construct a network client"),
    )
    with pytest.raises(RuntimeError, match="loopback"):
        probe.probe_phase_status(host=host, port=8000, timeout=2)


@pytest.mark.parametrize("port", [0, -1, 65536, "abc", "80/path"])
def test_readiness_probe_rejects_invalid_port_before_opener(monkeypatch, port):
    probe = _load_probe()
    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda *_args: pytest.fail("denial must not construct a network client"),
    )
    with pytest.raises(RuntimeError, match="port"):
        probe.probe_phase_status(host="127.0.0.1", port=port, timeout=2)


def test_readiness_probe_disables_proxy_and_redirects(monkeypatch):
    probe = _load_probe()
    handlers = []
    requests = []

    class _Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    class _Opener:
        def open(self, request, timeout):
            requests.append((request, timeout))
            return _Response()

    def _build_opener(*items):
        handlers.extend(items)
        return _Opener()

    monkeypatch.setattr(urllib.request, "build_opener", _build_opener)
    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: pytest.fail("global proxy-aware urlopen is forbidden"),
    )

    assert probe.probe_phase_status(host="127.0.0.1", port=8000, timeout=2)
    proxy_handlers = [item for item in handlers if isinstance(item, urllib.request.ProxyHandler)]
    redirect_handlers = [
        item for item in handlers if isinstance(item, urllib.request.HTTPRedirectHandler)
    ]
    assert len(proxy_handlers) == 1
    assert proxy_handlers[0].proxies == {}
    assert len(redirect_handlers) == 1
    request, timeout = requests[0]
    assert request.full_url == "http://127.0.0.1:8000/phase-status"
    assert request.method == "GET"
    assert timeout == 2


def test_readiness_probe_reaches_direct_loopback_server():
    probe = _load_probe()

    class _ReadyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            assert self.path == "/phase-status"
            self.send_response(200)
            self.end_headers()

        def log_message(self, *_args):
            pass

    server = HTTPServer(("127.0.0.1", 0), _ReadyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert probe.probe_phase_status(
            host="127.0.0.1",
            port=server.server_port,
            timeout=2,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_readiness_probe_does_not_follow_redirect():
    probe = _load_probe()
    redirected_requests = []

    class _RedirectTarget(BaseHTTPRequestHandler):
        def do_GET(self):
            redirected_requests.append(self.path)
            self.send_response(200)
            self.end_headers()

        def log_message(self, *_args):
            pass

    target = HTTPServer(("127.0.0.1", 0), _RedirectTarget)
    target_thread = threading.Thread(target=target.serve_forever, daemon=True)
    target_thread.start()

    class _RedirectHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header(
                "Location",
                f"http://127.0.0.1:{target.server_port}/redirected",
            )
            self.end_headers()

        def log_message(self, *_args):
            pass

    source = HTTPServer(("127.0.0.1", 0), _RedirectHandler)
    source_thread = threading.Thread(target=source.serve_forever, daemon=True)
    source_thread.start()
    try:
        assert not probe.probe_phase_status(
            host="127.0.0.1",
            port=source.server_port,
            timeout=2,
        )
        assert redirected_requests == []
    finally:
        source.shutdown()
        source.server_close()
        source_thread.join(timeout=2)
        target.shutdown()
        target.server_close()
        target_thread.join(timeout=2)

