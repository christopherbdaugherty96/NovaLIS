from src.actions.action_request import ActionRequest
from src.executors.brightness_executor import BrightnessExecutor
from src.executors.media_executor import MediaExecutor
from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor
from src.executors.volume_executor import VolumeExecutor


def test_media_executor_uses_system_control(monkeypatch):
    executor = MediaExecutor()
    seen: dict[str, str] = {}

    def fake_control(action: str) -> bool:
        seen["action"] = action
        return True

    monkeypatch.setattr(executor.system_control, "control_media", fake_control)
    result = executor.execute(ActionRequest(capability_id=20, params={"action": "pause"}))

    assert result.success is True
    assert seen["action"] == "pause"
    assert result.message == "Playback paused."


def test_brightness_executor_uses_system_control_for_set(monkeypatch):
    executor = BrightnessExecutor()
    seen: dict[str, int] = {}

    def fake_brightness(action: str, level: int | None = None) -> bool:
        seen["level"] = int(level or -1)
        return True

    monkeypatch.setattr(executor.system_control, "set_brightness", fake_brightness)
    result = executor.execute(ActionRequest(capability_id=21, params={"action": "set", "level": 65}))

    assert result.success is True
    assert seen["level"] == 65
    assert result.message == "Set brightness to 65%."


def test_volume_executor_supports_mute(monkeypatch):
    executor = VolumeExecutor()
    seen: dict[str, str] = {}

    def fake_volume(action: str, level: int | None = None) -> bool:
        del level
        seen["action"] = action
        return True

    monkeypatch.setattr(executor.system_control, "set_volume", fake_volume)
    result = executor.execute(ActionRequest(capability_id=19, params={"action": "mute"}))

    assert result.success is True
    assert seen["action"] == "mute"
    assert result.message == "Audio muted."


def test_media_executor_fails_when_system_control_cannot_apply(monkeypatch):
    executor = MediaExecutor()
    monkeypatch.setattr(executor.system_control, "control_media", lambda *_args, **_kwargs: False)

    result = executor.execute(ActionRequest(capability_id=20, params={"action": "pause"}))

    assert result.success is False
    assert "couldn't pause" in result.message.lower()


def test_volume_executor_fails_when_system_control_cannot_apply(monkeypatch):
    executor = VolumeExecutor()

    monkeypatch.setattr(executor.system_control, "set_volume", lambda *_args, **_kwargs: False)
    result = executor.execute(ActionRequest(capability_id=19, params={"action": "set", "level": 40}))

    assert result.success is False
    assert "couldn't set volume" in result.message.lower()


def test_os_diagnostics_executor_returns_extended_metrics(monkeypatch):
    import src.executors.os_diagnostics_executor as mod

    class _Disk:
        total = 500 * (1024 ** 3)
        used = 250 * (1024 ** 3)
        free = 250 * (1024 ** 3)

    class _Mem:
        total = 32 * (1024 ** 3)
        used = 16 * (1024 ** 3)
        available = 16 * (1024 ** 3)
        percent = 50.0

    class _Swap:
        total = 8 * (1024 ** 3)
        used = 1 * (1024 ** 3)
        percent = 12.5

    class _Iface:
        isup = True

    monkeypatch.setattr(mod.shutil, "disk_usage", lambda _path: _Disk())
    monkeypatch.setattr(mod.psutil, "virtual_memory", lambda: _Mem())
    monkeypatch.setattr(mod.psutil, "swap_memory", lambda: _Swap())
    monkeypatch.setattr(mod.psutil, "cpu_percent", lambda interval=0.0: 24.7)
    monkeypatch.setattr(mod.psutil, "boot_time", lambda: mod.time.time() - 7200.0)
    monkeypatch.setattr(mod.psutil, "pids", lambda: [1, 2, 3, 4])
    monkeypatch.setattr(mod.psutil, "net_if_stats", lambda: {"Ethernet": _Iface()})
    monkeypatch.setattr(
        mod.OSDiagnosticsExecutor,
        "_memory_status_details",
        staticmethod(lambda: ("enabled", 3, "2026-03-13T12:00:00+00:00", "Persistent memory enabled with 3 item(s).")),
    )
    monkeypatch.setattr(
        mod.OSDiagnosticsExecutor,
        "_policy_status_details",
        staticmethod(lambda: ("manual_review_ready", "2 draft policy item(s)", 2, 2, 0, 3, 1)),
    )
    monkeypatch.setattr(
        mod.OSDiagnosticsExecutor,
        "_ledger_status_details",
        staticmethod(lambda: ("ok", 24, "SEARCH_EXECUTED")),
    )

    result = OSDiagnosticsExecutor().execute(ActionRequest(capability_id=32, params={}))

    assert result.success is True
    assert "system checks complete" in result.message.lower()
    assert isinstance(result.data, dict)
    assert result.speakable_text == result.message
    assert isinstance(result.structured_data, dict)
    assert result.data.get("cpu_percent") == 24.7
    assert result.data.get("memory_percent") == 50.0
    assert result.data.get("disk_percent") == 50.0
    assert result.data.get("network_status") == "available"
    assert result.data.get("health_state") == "healthy"
    assert result.data.get("phase_display") == "7 complete / 8 design"
    assert result.data.get("governor_status") == "active"
    assert result.data.get("execution_boundary_status") == "enforced"
    assert result.data.get("memory_total_count") == 3
    assert result.data.get("policy_draft_count") == 2
    assert result.data.get("policy_simulation_count") == 3
    assert result.data.get("policy_manual_run_count") == 1
    assert result.data.get("ledger_entries_today") == 24
    assert isinstance(result.data.get("blocked_conditions"), list)
    assert isinstance(result.data.get("system_reasons"), list)
    assert "Locks" in str(result.data.get("operator_health_summary") or "")
    assert result.structured_data.get("health_state") == "healthy"


def test_os_diagnostics_recent_activity_marks_unsuccessful_action_as_issue():
    item = OSDiagnosticsExecutor._recent_activity_item(
        {
            "_ledger_line": 42,
            "event_type": "ACTION_COMPLETED",
            "capability_id": 31,
            "request_id": "req-verify-123",
            "success": False,
            "failure_reason": "Model inference is blocked in this runtime.",
            "external_effect": False,
            "reversible": True,
            "timestamp_utc": "2026-03-19T03:43:11+00:00",
        },
        {31: "response verification"},
    )

    assert item is not None
    assert item["title"] == "Action needs attention"
    assert item["detail"] == "response verification"
    assert item["outcome"] == "issue"
    assert item["reason"] == "Model inference is blocked in this runtime."
    assert item["effect"] == "No external effect, Reversible"
    assert item["request_id"] == "req-verify-123"
    assert item["ledger_ref"] == "L42"


def test_os_diagnostics_recent_activity_uses_status_and_outcome_reason_when_success_missing():
    item = OSDiagnosticsExecutor._recent_activity_item(
        {
            "_ledger_line": 43,
            "event_type": "ACTION_COMPLETED",
            "capability_id": 60,
            "request_id": "req-explain-456",
            "status": "failed",
            "outcome_reason": "Screen capture is unavailable in this runtime because the required dependency 'pyautogui' is missing.",
            "external_effect": False,
            "reversible": True,
            "timestamp_utc": "2026-03-19T03:49:11+00:00",
        },
        {60: "explain anything"},
    )

    assert item is not None
    assert item["title"] == "Action needs attention"
    assert item["outcome"] == "issue"
    assert "pyautogui" in item["reason"]
    assert item["request_id"] == "req-explain-456"
    assert item["ledger_ref"] == "L43"


def test_os_diagnostics_recent_activity_surfaces_allow_reason_for_successful_action():
    item = OSDiagnosticsExecutor._recent_activity_item(
        {
            "_ledger_line": 57,
            "event_type": "ACTION_COMPLETED",
            "capability_id": 16,
            "request_id": "req-search-456",
            "success": True,
            "authority_class": "read_only_network",
            "requires_confirmation": False,
            "external_effect": False,
            "reversible": True,
            "timestamp_utc": "2026-03-19T04:05:00+00:00",
        },
        {16: "governed web search"},
    )

    assert item is not None
    assert item["title"] == "Action completed"
    assert item["detail"] == "governed web search"
    assert item["outcome"] == "success"
    assert item["reason"] == "Allowed as an explicit read-only network action."
    assert item["effect"] == "No external effect, Reversible"
    assert item["request_id"] == "req-search-456"
    assert item["ledger_ref"] == "L57"


def test_os_diagnostics_executor_handles_network_stat_errors(monkeypatch):
    import src.executors.os_diagnostics_executor as mod

    class _Disk:
        total = 200 * (1024 ** 3)
        used = 190 * (1024 ** 3)
        free = 10 * (1024 ** 3)

    class _Mem:
        total = 16 * (1024 ** 3)
        used = 14 * (1024 ** 3)
        available = 2 * (1024 ** 3)
        percent = 88.0

    class _Swap:
        total = 4 * (1024 ** 3)
        used = 2 * (1024 ** 3)
        percent = 50.0

    monkeypatch.setattr(mod.shutil, "disk_usage", lambda _path: _Disk())
    monkeypatch.setattr(mod.psutil, "virtual_memory", lambda: _Mem())
    monkeypatch.setattr(mod.psutil, "swap_memory", lambda: _Swap())
    monkeypatch.setattr(mod.psutil, "cpu_percent", lambda interval=0.0: 92.0)
    monkeypatch.setattr(mod.psutil, "boot_time", lambda: mod.time.time() - 300.0)
    monkeypatch.setattr(mod.psutil, "pids", lambda: [1, 2])
    monkeypatch.setattr(mod.psutil, "net_if_stats", lambda: (_ for _ in ()).throw(RuntimeError("no stats")))

    result = OSDiagnosticsExecutor().execute(ActionRequest(capability_id=32, params={}))

    assert result.success is True
    assert result.data.get("network_status") == "unknown"
    assert result.data.get("health_state") == "critical"


def test_os_diagnostics_executor_includes_tone_summary(monkeypatch):
    import src.executors.os_diagnostics_executor as mod

    class _Disk:
        total = 200 * (1024 ** 3)
        used = 50 * (1024 ** 3)
        free = 150 * (1024 ** 3)

    class _Mem:
        total = 16 * (1024 ** 3)
        used = 5 * (1024 ** 3)
        available = 11 * (1024 ** 3)
        percent = 31.0

    class _Swap:
        total = 4 * (1024 ** 3)
        used = 0
        percent = 0.0

    class _Iface:
        isup = True

    monkeypatch.setattr(mod.shutil, "disk_usage", lambda _path: _Disk())
    monkeypatch.setattr(mod.psutil, "virtual_memory", lambda: _Mem())
    monkeypatch.setattr(mod.psutil, "swap_memory", lambda: _Swap())
    monkeypatch.setattr(mod.psutil, "cpu_percent", lambda interval=0.0: 18.0)
    monkeypatch.setattr(mod.psutil, "boot_time", lambda: mod.time.time() - 3600.0)
    monkeypatch.setattr(mod.psutil, "pids", lambda: [1, 2, 3])
    monkeypatch.setattr(mod.psutil, "net_if_stats", lambda: {"Ethernet": _Iface()})
    monkeypatch.setattr(
        mod.OSDiagnosticsExecutor,
        "_tone_status_details",
        staticmethod(lambda: ("formal", "Global tone: formal. Overrides: Research and analysis: detailed.", "2026-03-13T12:00:00+00:00", 1)),
    )

    result = OSDiagnosticsExecutor().execute(ActionRequest(capability_id=32, params={}))

    assert result.success is True
    assert result.data.get("tone_global_profile") == "formal"
    assert "Global tone: formal." in str(result.data.get("tone_summary") or "")
    assert "tone formal" in result.message.lower()


def test_os_diagnostics_executor_includes_notification_policy_summary(monkeypatch):
    import src.executors.os_diagnostics_executor as mod

    class _Disk:
        total = 200 * (1024 ** 3)
        used = 50 * (1024 ** 3)
        free = 150 * (1024 ** 3)

    class _Mem:
        total = 16 * (1024 ** 3)
        used = 5 * (1024 ** 3)
        available = 11 * (1024 ** 3)
        percent = 31.0

    class _Swap:
        total = 4 * (1024 ** 3)
        used = 0
        percent = 0.0

    class _Iface:
        isup = True

    monkeypatch.setattr(mod.shutil, "disk_usage", lambda _path: _Disk())
    monkeypatch.setattr(mod.psutil, "virtual_memory", lambda: _Mem())
    monkeypatch.setattr(mod.psutil, "swap_memory", lambda: _Swap())
    monkeypatch.setattr(mod.psutil, "cpu_percent", lambda interval=0.0: 18.0)
    monkeypatch.setattr(mod.psutil, "boot_time", lambda: mod.time.time() - 3600.0)
    monkeypatch.setattr(mod.psutil, "pids", lambda: [1, 2, 3])
    monkeypatch.setattr(mod.psutil, "net_if_stats", lambda: {"Ethernet": _Iface()})
    monkeypatch.setattr(
        mod.OSDiagnosticsExecutor,
        "_notification_schedule_details",
        staticmethod(lambda: ("Quiet hours: 10:00 PM to 7:00 AM. Rate limit: 2 per hour. Delivered last hour: 1.", True, "10:00 PM to 7:00 AM", 2, 3, 1)),
    )

    result = OSDiagnosticsExecutor().execute(ActionRequest(capability_id=32, params={}))

    assert result.success is True
    assert "quiet hours: 10:00 pm to 7:00 am" in str(result.data.get("notification_policy_summary") or "").lower()
    assert result.data.get("notification_rate_limit_per_hour") == 2
    assert "notifications 10:00 pm to 7:00 am" in result.message.lower()


def test_os_diagnostics_executor_reports_blocked_model_as_not_ready(monkeypatch):
    import src.executors.os_diagnostics_executor as mod
    import src.llm.llm_manager as llm_mod

    class _Disk:
        total = 200 * (1024 ** 3)
        used = 80 * (1024 ** 3)
        free = 120 * (1024 ** 3)

    class _Mem:
        total = 16 * (1024 ** 3)
        used = 4 * (1024 ** 3)
        available = 12 * (1024 ** 3)
        percent = 25.0

    class _Swap:
        total = 4 * (1024 ** 3)
        used = 0
        percent = 0.0

    class _Iface:
        isup = True

    monkeypatch.setattr(mod.shutil, "disk_usage", lambda _path: _Disk())
    monkeypatch.setattr(mod.psutil, "virtual_memory", lambda: _Mem())
    monkeypatch.setattr(mod.psutil, "swap_memory", lambda: _Swap())
    monkeypatch.setattr(mod.psutil, "cpu_percent", lambda interval=0.0: 12.0)
    monkeypatch.setattr(mod.psutil, "boot_time", lambda: mod.time.time() - 600.0)
    monkeypatch.setattr(mod.psutil, "pids", lambda: [1, 2, 3])
    monkeypatch.setattr(mod.psutil, "net_if_stats", lambda: {"Ethernet": _Iface()})
    monkeypatch.setattr(llm_mod.llm_manager, "health_check", lambda: True)
    monkeypatch.setattr(llm_mod.llm_manager, "inference_blocked", True)

    result = OSDiagnosticsExecutor().execute(ActionRequest(capability_id=32, params={}))

    assert result.success is True
    assert result.data.get("model_availability") == "blocked"
    assert result.data.get("model_ready") is False
    assert "confirm model update" in result.data.get("model_remediation", "").lower()
    assert "locked pending explicit confirmation" in result.data.get("model_note", "").lower()
