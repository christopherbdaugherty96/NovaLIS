import pytest

from src.governor.exceptions import NetworkMediatorError
from src.governor.network_mediator import NetworkMediator


def test_plain_http_blocked_by_default():
    mediator = NetworkMediator()
    with pytest.raises(NetworkMediatorError, match="Plain HTTP is blocked"):
        mediator._validate_url("http://example.com/feed")


def test_plain_http_allowed_only_for_explicit_exception_host(monkeypatch):
    monkeypatch.setenv("NOVA_HTTP_EXCEPTION_HOSTS", "example.com")
    mediator = NetworkMediator()
    mediator._validate_url("http://example.com/feed")
