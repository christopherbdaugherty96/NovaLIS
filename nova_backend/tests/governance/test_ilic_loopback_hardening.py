from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from src.llm.ilic import (
    ILICValidationError,
    validate_and_lock_base_url,
    build_hardened_session,
)
from src.llm import inference_wrapper


def test_ilic_base_url_accepts_only_loopback_defaults():
    locked = validate_and_lock_base_url("http://localhost:11434")
    assert locked.host == "localhost"
    assert locked.port == 11434

    locked_ip = validate_and_lock_base_url("http://127.0.0.1:11434")
    assert locked_ip.host == "127.0.0.1"


@pytest.mark.parametrize(
    "url",
    [
        "https://localhost:11434",
        "http://localhost:9999",
        "http://example.com:11434",
        "http://10.0.0.5:11434",
        "http://localhost:11434/path",
        "http://localhost:11434?x=1",
    ],
)
def test_ilic_base_url_rejects_nonconforming_values(url: str):
    with pytest.raises(ILICValidationError):
        validate_and_lock_base_url(url)


def test_ilic_session_disables_proxy_env_usage():
    session = build_hardened_session()
    assert session.trust_env is False
    assert session.proxies == {}


def test_ilic_dns_resolution_fail_closed(monkeypatch):
    def fake_getaddrinfo(host, port):
        return [(None, None, None, None, ("8.8.8.8", 0))]

    monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)
    with pytest.raises(ILICValidationError):
        validate_and_lock_base_url("http://localhost:11434")


def test_inference_wrapper_rejects_external_base_url_before_request():
    with pytest.raises(ILICValidationError):
        inference_wrapper.run_inference(
            base_url="http://example.com:11434",
            model="phi3:mini",
            prompt="hello",
            system="sys",
            options={},
            timeout=(1.0, 1.0),
            allow_redirects=False,
            trust_env=False,
        )
