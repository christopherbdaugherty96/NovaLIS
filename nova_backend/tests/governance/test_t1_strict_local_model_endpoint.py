from __future__ import annotations

import pytest
from src.llm.model_network_mediator import ModelNetworkMediator, ModelNetworkMediatorError


@pytest.mark.parametrize(
    "url",
    (
        "http://192.168.1.20:11434/api/chat",
        "http://169.254.10.20:11434/api/chat",
        "http://10.0.0.5:11434/api/chat",
    ),
)
def test_trial_rejects_non_loopback_model_endpoint_before_transport(monkeypatch, url):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    mediator = ModelNetworkMediator()
    calls = []
    monkeypatch.setattr(
        mediator,
        "_request_session",
        lambda: calls.append("transport") or pytest.fail("transport must not be selected"),
    )

    with pytest.raises(ModelNetworkMediatorError, match="loopback"):
        mediator.request_json(method="POST", url=url, json_payload={"prompt": "private"})

    assert calls == []


@pytest.mark.parametrize(
    "url",
    ("http://localhost:11434/api/chat", "http://127.0.0.1:11434/api/chat", "http://[::1]:11434/api/chat"),
)
def test_trial_preserves_loopback_model_endpoints(monkeypatch, url):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    mediator = ModelNetworkMediator()

    mediator._validate_url(url)


def test_trial_rejects_localhost_when_dns_resolves_off_loopback(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    monkeypatch.setattr(
        "src.llm.model_network_mediator.socket.getaddrinfo",
        lambda *_args, **_kwargs: [(2, 1, 6, "", ("192.168.1.20", 0))],
    )
    mediator = ModelNetworkMediator()

    with pytest.raises(ModelNetworkMediatorError, match="loopback"):
        mediator._validate_url("http://localhost:11434/api/chat")


def test_default_profile_still_allows_private_lan_model_endpoint(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "default")
    mediator = ModelNetworkMediator()

    mediator._validate_url("http://192.168.1.20:11434/api/chat")


def test_trial_model_sessions_ignore_environment_proxies(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    monkeypatch.setenv("HTTP_PROXY", "http://192.168.1.25:8888")
    monkeypatch.setenv("NO_PROXY", "")
    mediator = ModelNetworkMediator()

    assert mediator._request_session().trust_env is False


@pytest.mark.parametrize("streaming", (False, True))
def test_trial_model_requests_disable_redirects(monkeypatch, streaming):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    mediator = ModelNetworkMediator()
    captured = {}

    class _Response:
        status_code = 200
        content = b"{}"

        def raise_for_status(self):
            return None

        def json(self):
            return {}

        def iter_lines(self, decode_unicode=False):
            del decode_unicode
            return iter((b'{"done": true, "done_reason": "stop"}',))

        def close(self):
            return None

    class _Session:
        def request(self, **kwargs):
            captured.update(kwargs)
            return _Response()

        def post(self, _url, **kwargs):
            captured.update(kwargs)
            return _Response()

    monkeypatch.setattr(mediator, "_request_session", lambda: _Session())

    if streaming:
        list(mediator.request_stream(url="http://localhost:11434/api/chat", json_payload={"secret": 1}))
    else:
        mediator.request_json(
            method="POST",
            url="http://localhost:11434/api/chat",
            json_payload={"secret": 1},
        )

    assert captured["allow_redirects"] is False


@pytest.mark.parametrize("streaming", (False, True))
def test_trial_model_transport_uses_validated_loopback_ip(monkeypatch, streaming):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    monkeypatch.setattr(
        "src.llm.model_network_mediator.socket.getaddrinfo",
        lambda *_args, **_kwargs: [(2, 1, 6, "", ("127.0.0.1", 0))],
    )
    mediator = ModelNetworkMediator()
    captured = {}

    class _Response:
        status_code = 200
        content = b"{}"

        def raise_for_status(self):
            return None

        def json(self):
            return {}

        def iter_lines(self, decode_unicode=False):
            del decode_unicode
            return iter((b'{"done": true, "done_reason": "stop"}',))

        def close(self):
            return None

    class _Session:
        def request(self, **kwargs):
            captured.update(kwargs)
            return _Response()

        def post(self, url, **kwargs):
            captured["url"] = url
            captured.update(kwargs)
            return _Response()

    monkeypatch.setattr(mediator, "_request_session", lambda: _Session())

    if streaming:
        list(mediator.request_stream(url="http://localhost:11434/api/chat", json_payload={}))
    else:
        mediator.request_json(method="POST", url="http://localhost:11434/api/chat", json_payload={})

    assert captured["url"] == "http://127.0.0.1:11434/api/chat"
