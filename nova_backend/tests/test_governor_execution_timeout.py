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


def test_governor_cpu_cap_fails_closed_and_logs_event(monkeypatch):
    from src.actions.action_result import ActionResult
    from src.governor.governor import Governor
    from src.governor.execute_boundary.execute_boundary import ExecutionCPUExceededError

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

    # Simulate successful executor return, then boundary CPU enforcement failure.
    monkeypatch.setattr(
        gov,
        "_dispatch_capability",
        lambda req: ActionResult.ok("executor succeeded", data={"leak": True}, request_id=req.request_id),
    )
    monkeypatch.setattr(
        gov._execute_boundary,
        "enforce_cpu_limits",
        lambda: (_ for _ in ()).throw(ExecutionCPUExceededError("cpu cap exceeded")),
    )

    result = gov.handle_governed_invocation(19, {"action": "up"})

    # 1) Execution fails closed.
    assert result.success is False
    assert "exceeded allowed cpu budget" in result.message.lower()

    # 2) No partial success payload leaks through.
    assert result.data is None

    # 3) Correct ledger event is emitted.
    assert any(e[0] == "EXECUTION_CPU_EXCEEDED" for e in gov._ledger.events)

    # Ensure no successful completion event leaked.
    assert not any(
        event == "ACTION_COMPLETED" and bool(meta.get("success")) is True
        for event, meta in gov._ledger.events
    )


def test_governor_action_completed_logs_failure_reason_and_effect_metadata(monkeypatch):
    from src.actions.action_result import ActionResult
    from src.governor.governor import Governor

    gov = Governor()

    class FakeRegistry:
        def get(self, capability_id):
            return types.SimpleNamespace(name="fake")

        def is_enabled(self, capability_id):
            return True

    class FakeLedger:
        def __init__(self):
            self.events = []

        def log_event(self, event_type, metadata):
            self.events.append((event_type, metadata))

    gov._registry = FakeRegistry()
    gov._ledger = FakeLedger()
    gov._capability_topology = types.SimpleNamespace(
        get=lambda _capability_id: types.SimpleNamespace(
            authority_class="read_only_local",
            requires_confirmation=False,
        )
    )

    monkeypatch.setattr(
        gov,
        "_dispatch_capability",
        lambda req: ActionResult.failure(
            "Model inference is blocked in this runtime.",
            request_id=req.request_id,
            external_effect=False,
            reversible=True,
        ),
    )

    result = gov.handle_governed_invocation(31, {"text": "fact check this"})

    assert result.success is False
    completed = [meta for event, meta in gov._ledger.events if event == "ACTION_COMPLETED"]
    assert completed
    payload = completed[-1]
    assert payload["success"] is False
    assert payload["failure_reason"] == "Model inference is blocked in this runtime."
    assert payload["external_effect"] is False
    assert payload["reversible"] is True
    assert payload["authority_class"] == "read_only_local"
    assert payload["requires_confirmation"] is False


def test_governor_uses_extended_timeout_for_response_verification(monkeypatch):
    from src.actions.action_result import ActionResult
    from src.governor.governor import Governor

    gov = Governor()

    class FakeRegistry:
        def get(self, capability_id):
            return types.SimpleNamespace(name="response_verification")

        def is_enabled(self, capability_id):
            return True

    class FakeLedger:
        def __init__(self):
            self.events = []

        def log_event(self, event_type, metadata):
            self.events.append((event_type, metadata))

    captured = {}
    gov._registry = FakeRegistry()
    gov._ledger = FakeLedger()

    monkeypatch.setattr(
        gov,
        "_dispatch_capability",
        lambda req: ActionResult.ok("verified", request_id=req.request_id),
    )

    def _fake_run_with_timeout(operation, timeout_seconds=None):
        captured["timeout_seconds"] = timeout_seconds
        return operation()

    monkeypatch.setattr(gov._execute_boundary, "run_with_timeout", _fake_run_with_timeout)

    result = gov.handle_governed_invocation(31, {"text": "fact check this"})

    assert result.success is True
    assert captured["timeout_seconds"] == 90.0


def test_governor_uses_extended_timeout_for_analysis_document(monkeypatch):
    from src.actions.action_result import ActionResult
    from src.governor.governor import Governor

    gov = Governor()

    class FakeRegistry:
        def get(self, capability_id):
            return types.SimpleNamespace(name="analysis_document")

        def is_enabled(self, capability_id):
            return True

    class FakeLedger:
        def __init__(self):
            self.events = []

        def log_event(self, event_type, metadata):
            self.events.append((event_type, metadata))

    captured = {}
    gov._registry = FakeRegistry()
    gov._ledger = FakeLedger()

    monkeypatch.setattr(
        gov,
        "_dispatch_capability",
        lambda req: ActionResult.ok("created", request_id=req.request_id),
    )

    def _fake_run_with_timeout(operation, timeout_seconds=None):
        captured["timeout_seconds"] = timeout_seconds
        return operation()

    monkeypatch.setattr(gov._execute_boundary, "run_with_timeout", _fake_run_with_timeout)

    result = gov.handle_governed_invocation(54, {"action": "create", "topic": "AI geopolitics"})

    assert result.success is True
    assert captured["timeout_seconds"] == 150.0
