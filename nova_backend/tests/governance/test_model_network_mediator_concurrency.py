from __future__ import annotations

import threading
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

    # Both request threads must be inside the session's request() at the same time for the
    # barrier to trip. If the mediator serialized the waits, only one thread would arrive and
    # the barrier would time out (BrokenBarrierError). This proves concurrency directly via
    # synchronization evidence instead of a load-sensitive wall-clock threshold.
    entered_together = threading.Barrier(2, timeout=2.0)
    overlap = {"concurrent": False, "broken": False}

    class _OverlappingSession:
        def request(self, **_kwargs):
            try:
                entered_together.wait()
                overlap["concurrent"] = True
            except threading.BrokenBarrierError:
                overlap["broken"] = True
            return _Response()

    mediator = ModelNetworkMediator()
    mediator._ledger = SimpleNamespace(log_event=lambda *_args, **_kwargs: None)
    mediator._session = _OverlappingSession()

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
        thread.join(timeout=3.0)

    assert all(not thread.is_alive() for thread in threads), "request threads did not finish"
    assert overlap["concurrent"] and not overlap["broken"], (
        "overlapping request waits were serialized: both requests did not enter the mediator "
        "waiting section concurrently"
    )
