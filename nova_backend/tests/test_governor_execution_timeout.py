import types


def test_governor_timeout_returns_refusal(monkeypatch):
    from src.governor.governor import Governor

    gov = Governor()

    class FakeRegistry:
        def get(self, capability_id):
            return types.SimpleNamespace(name="fake")

        def is_enabled(self, capability_id):
            return True

    gov._registry = FakeRegistry()

    class FakeLedger:
        def __init__(self):
            self.events = []

        def log_event(self, event_type, metadata):
            self.events.append((event_type, metadata))

    gov._ledger = FakeLedger()

    # Simulate elapsed time > MAX_EXECUTION_TIME
    timeline = iter([0.0, 12.5])
    monkeypatch.setattr("src.governor.governor.time.monotonic", lambda: next(timeline))

    class FakeExecutor:
        def execute(self, req):
            from src.actions.action_result import ActionResult
            return ActionResult.ok("done", request_id=req.request_id)

    monkeypatch.setattr("src.executors.volume_executor.VolumeExecutor", lambda: FakeExecutor())

    result = gov.handle_governed_invocation(19, {"action": "up"})
    assert result.success is False
    assert "exceeded allowed time" in result.message.lower()
    assert any(e[0] == "EXECUTION_TIMEOUT" for e in gov._ledger.events)


def test_governor_memory_cap_fails_closed_and_logs_event(monkeypatch):
    from src.actions.action_result import ActionResult
    from src.governor.governor import Governor

    gov = Governor()

    class FakeRegistry:
        def get(self, capability_id):
            return types.SimpleNamespace(name="fake")

        def is_enabled(self, capability_id):
            return True

    gov._registry = FakeRegistry()

    class FakeLedger:
        def __init__(self):
            self.events = []

        def log_event(self, event_type, metadata):
            self.events.append((event_type, metadata))

    gov._ledger = FakeLedger()

    # Simulate successful executor return, then boundary memory enforcement failure.
    monkeypatch.setattr(
        gov,
        "_dispatch_capability",
        lambda req: ActionResult.ok("executor succeeded", data={"leak": True}, request_id=req.request_id),
    )
    monkeypatch.setattr(
        gov._execute_boundary,
        "enforce_memory_limits",
        lambda: (_ for _ in ()).throw(MemoryError("cap exceeded")),
    )

    result = gov.handle_governed_invocation(19, {"action": "up"})

    # 1) Execution fails closed.
    assert result.success is False
    assert "exceeded allowed memory" in result.message.lower()

    # 2) No partial success payload leaks through.
    assert result.data is None

    # 3) Correct ledger event is emitted.
    assert any(e[0] == "EXECUTION_MEMORY_EXCEEDED" for e in gov._ledger.events)

    # Ensure no successful completion event leaked.
    assert not any(
        event == "ACTION_COMPLETED" and bool(meta.get("success")) is True
        for event, meta in gov._ledger.events
    )
