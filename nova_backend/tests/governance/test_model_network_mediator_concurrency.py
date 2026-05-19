from __future__ import annotations

import threading
import time
from types import SimpleNamespace


def test_model_network_mediator_allows_overlapping_request_waits():
    from src.llm.model_network_mediator import ModelNetworkMediator

    class _Response:
        status_code = 200
        content = b'{"ok": true}'

        @staticmethod
        def json() -> dict:
            return {"ok": True}

        @staticmethod
        def raise_for_status() -> None:
            return None

    class _SlowSession:
        def request(self, **_kwargs):
            time.sleep(0.15)
            return _Response()

    mediator = ModelNetworkMediator()
    mediator._ledger = SimpleNamespace(log_event=lambda *_args, **_kwargs: None)
    mediator._session = _SlowSession()

    started_at = time.perf_counter()
    threads = [
        threading.Thread(
            target=mediator.request_json,
            kwargs={
                "method": "POST",
                "url": "http://localhost:11434/api/chat",
                "json_payload": {"ping": "pong"},
                "timeout": 2.0,
            },
        )
        for _ in range(2)
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=1.0)

    assert all(not thread.is_alive() for thread in threads)
    assert time.perf_counter() - started_at < 0.27
