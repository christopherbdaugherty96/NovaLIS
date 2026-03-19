from __future__ import annotations

from pathlib import Path

from src.actions.action_request import ActionRequest
from src.executors.open_folder_executor import OpenFolderExecutor


def test_open_folder_executor_opens_explicit_existing_path(monkeypatch, tmp_path: Path):
    executor = OpenFolderExecutor()
    target = tmp_path / "notes"
    target.mkdir()

    monkeypatch.setattr(executor.system_control, "open_path", lambda path: path == target)
    result = executor.execute(ActionRequest(capability_id=22, params={"path": str(target)}))

    assert result.success is True
    assert str(target) in result.message
    assert result.data["path"] == str(target)


def test_open_folder_executor_fails_for_missing_explicit_path(tmp_path: Path):
    executor = OpenFolderExecutor()
    target = tmp_path / "missing"

    result = executor.execute(ActionRequest(capability_id=22, params={"path": str(target)}))

    assert result.success is False
    assert "couldn't find that path" in result.message.lower()


def test_open_folder_executor_opens_preset_folder(monkeypatch, tmp_path: Path):
    executor = OpenFolderExecutor()
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    monkeypatch.setattr("src.executors.open_folder_executor.PRESET_FOLDERS", {"downloads": downloads})
    monkeypatch.setattr(executor.system_control, "open_path", lambda path: path == downloads)

    result = executor.execute(ActionRequest(capability_id=22, params={"target": "downloads"}))

    assert result.success is True
    assert "Opened your downloads folder" in result.message
    assert result.data["path"] == str(downloads)
