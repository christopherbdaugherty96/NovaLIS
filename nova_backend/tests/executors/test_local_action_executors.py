from __future__ import annotations

from pathlib import Path

from src.actions.action_request import ActionRequest
from src.executors.media_executor import MediaExecutor
from src.executors.open_folder_executor import OpenFolderExecutor
from src.executors.volume_executor import VolumeExecutor


def test_volume_executor_handles_mute_on_windows(monkeypatch):
    executor = VolumeExecutor()
    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: "Windows")

    result = executor.execute(ActionRequest(capability_id=19, params={"action": "mute"}))

    assert result.success is True
    assert result.authority_class == "reversible_local"
    assert result.external_effect is False
    assert result.reversible is True


def test_media_executor_handles_pause_on_windows(monkeypatch):
    executor = MediaExecutor()
    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: "Windows")

    result = executor.execute(ActionRequest(capability_id=20, params={"action": "pause"}))

    assert result.success is True
    assert result.authority_class == "reversible_local"
    assert result.external_effect is False
    assert result.reversible is True


def test_open_folder_executor_returns_canonical_local_metadata(monkeypatch, tmp_path: Path):
    executor = OpenFolderExecutor()
    target = tmp_path / "notes"
    target.mkdir()

    monkeypatch.setattr(executor.system_control, "open_path", lambda path: path == target)
    result = executor.execute(ActionRequest(capability_id=22, params={"path": str(target)}))

    assert result.success is True
    assert result.authority_class == "reversible_local"
    assert result.external_effect is False
    assert result.reversible is True
