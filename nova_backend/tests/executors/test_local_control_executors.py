from src.actions.action_request import ActionRequest
from src.executors.brightness_executor import BrightnessExecutor
from src.executors.media_executor import MediaExecutor
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
