from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.governor.exceptions import NetworkMediatorError
from src.governor.network_mediator import NetworkMediator


class _FakeRegistry:
    def get(self, capability_id: int):
        return SimpleNamespace(name=f"cap-{capability_id}")

    def is_enabled(self, capability_id: int) -> bool:
        return True


def test_network_mediator_revalidates_redirect_targets(monkeypatch):
    mediator = NetworkMediator()
    mediator._registry = _FakeRegistry()

    class _Response:
        status_code = 302
        is_redirect = True
        is_permanent_redirect = False
        headers = {"Location": "http://127.0.0.1/internal"}
        content = b""
        text = ""

        def raise_for_status(self):
            return None

    def _fake_request(**kwargs):
        return _Response()

    monkeypatch.setattr("src.governor.network_mediator.requests.request", _fake_request)

    with pytest.raises(NetworkMediatorError, match="forbidden"):
        mediator.request(16, "GET", "https://example.com", as_json=False)
