from __future__ import annotations

import base64
import http.client
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


def _nonloopback_ipv4() -> str | None:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        candidate = probe.getsockname()[0]
    except OSError:
        return None
    finally:
        probe.close()
    return candidate if candidate and not candidate.startswith("127.") else None


def _free_port() -> int:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])
    finally:
        listener.close()


def _wait_until_ready(port: int) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
            connection.request("GET", "/phase-status", headers={"Host": f"localhost:{port}"})
            response = connection.getresponse()
            response.read()
            connection.close()
            if response.status == 200:
                return
        except OSError:
            time.sleep(0.2)
    raise AssertionError("temporary Nova server did not become ready")


def _websocket_handshake(connect_host: str, port: int) -> str:
    websocket_key = base64.b64encode(os.urandom(16)).decode("ascii")
    request = (
        "GET /ws HTTP/1.1\r\n"
        f"Host: localhost:{port}\r\n"
        f"Origin: http://localhost:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {websocket_key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    ).encode("ascii")
    with socket.create_connection((connect_host, port), timeout=30) as connection:
        connection.sendall(request)
        return connection.recv(4096).decode("utf-8", errors="replace")


@pytest.fixture(scope="module")
def exposed_server():
    peer = _nonloopback_ipv4()
    if not peer:
        pytest.skip("no non-loopback IPv4 interface is available for a real-peer proof")
    port = _free_port()
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "nova_backend")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "src.brain_server:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
            "--app-dir",
            str(ROOT / "nova_backend"),
            "--lifespan",
            "off",
        ],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_until_ready(port)
        yield peer, port
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


@pytest.mark.realnet
def test_nonloopback_tcp_peer_cannot_spoof_local_http_headers(exposed_server):
    peer, port = exposed_server
    connection = http.client.HTTPConnection(peer, port, timeout=5)
    connection.request(
        "GET",
        "/api/memory/export",
        headers={"Host": f"localhost:{port}", "Origin": f"http://localhost:{port}"},
    )
    response = connection.getresponse()
    body = response.read().decode("utf-8", errors="replace")
    connection.close()
    assert response.status == 403
    assert "socket peer" in body.lower()


@pytest.mark.realnet
def test_nonloopback_tcp_peer_cannot_spoof_local_websocket_headers(exposed_server):
    peer, port = exposed_server
    response = _websocket_handshake(peer, port)
    assert " 403 " in response.split("\r\n", 1)[0]


@pytest.mark.realnet
def test_loopback_tcp_peer_retains_local_http_access(exposed_server):
    _, port = exposed_server
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    connection.request(
        "GET",
        "/api/trust/receipts",
        headers={"Host": f"localhost:{port}", "Origin": f"http://localhost:{port}"},
    )
    response = connection.getresponse()
    response.read()
    connection.close()
    assert response.status == 200


@pytest.mark.realnet
def test_loopback_tcp_peer_retains_local_websocket_access(exposed_server):
    _, port = exposed_server
    response = _websocket_handshake("127.0.0.1", port)
    assert " 101 " in response.split("\r\n", 1)[0]
