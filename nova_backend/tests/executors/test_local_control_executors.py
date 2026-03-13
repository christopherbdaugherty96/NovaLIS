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
    assert result.message == "Brightness set to 65."


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

    result = OSDiagnosticsExecutor().execute(ActionRequest(capability_id=32, params={}))

    assert result.success is True
    assert "system checks complete" in result.message.lower()
    assert isinstance(result.data, dict)
    assert result.data.get("cpu_percent") == 24.7
    assert result.data.get("memory_percent") == 50.0
    assert result.data.get("disk_percent") == 50.0
    assert result.data.get("network_status") == "available"
    assert result.data.get("health_state") == "healthy"


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
