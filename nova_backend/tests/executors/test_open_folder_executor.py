from __future__ import annotations

from pathlib import Path

from src.actions.action_request import ActionRequest
from src.executors.open_folder_executor import OpenFolderExecutor
from src.system_control.system_control_executor import (
    OpenPathLaunchResult,
    OpenPathLaunchState,
)


def _launch_result(
    state: OpenPathLaunchState,
    reason: str = "test_launch_result",
    *,
    returncode: int | None = None,
) -> OpenPathLaunchResult:
    return OpenPathLaunchResult(state, reason, returncode=returncode)


def test_open_folder_executor_reports_accepted_unverified_for_explicit_folder(
    monkeypatch, tmp_path: Path
):
    executor = OpenFolderExecutor()
    target = tmp_path / "notes"
    target.mkdir()

    monkeypatch.setattr(
        executor.system_control,
        "open_path_result",
        lambda path: _launch_result(OpenPathLaunchState.ACCEPTED),
    )
    monkeypatch.setattr(executor, "_visible_folder_verified", lambda path: False)
    result = executor.execute(ActionRequest(capability_id=22, params={"path": str(target)}))

    assert result.success is True
    assert str(target) in result.message
    assert "open request sent" in result.message.lower()
    assert "couldn't verify" in result.message.lower()
    assert "file manager" in result.message.lower()
    assert "File Explorer" not in result.message
    assert not result.message.lower().startswith("opened")
    assert result.data["path"] == str(target)
    assert result.data["outcome_state"] == "accepted_unverified"
    assert result.data["launch_request_accepted"] is True
    assert result.data["visible_effect_verified"] is False


def test_open_folder_executor_fails_for_missing_explicit_path(tmp_path: Path):
    executor = OpenFolderExecutor()
    target = tmp_path / "missing"

    result = executor.execute(ActionRequest(capability_id=22, params={"path": str(target)}))

    assert result.success is False
    assert "couldn't find that path" in result.message.lower()
    assert result.data["outcome_state"] == "rejected"
    assert result.data["launch_request_accepted"] is False
    assert result.data["visible_effect_verified"] is False


def test_open_folder_executor_reports_accepted_unverified_for_preset_folder(
    monkeypatch, tmp_path: Path
):
    executor = OpenFolderExecutor()
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    monkeypatch.setattr("src.executors.open_folder_executor.PRESET_FOLDERS", {"downloads": downloads})
    monkeypatch.setattr(
        executor.system_control,
        "open_path_result",
        lambda path: _launch_result(OpenPathLaunchState.ACCEPTED),
    )
    monkeypatch.setattr(executor, "_visible_folder_verified", lambda path: False)

    result = executor.execute(ActionRequest(capability_id=22, params={"target": "downloads"}))

    assert result.success is True
    assert "Open request sent for Downloads" in result.message
    assert "couldn't verify" in result.message.lower()
    assert "file manager" in result.message.lower()
    assert "File Explorer" not in result.message
    assert result.data["path"] == str(downloads)
    assert result.data["outcome_state"] == "accepted_unverified"
    assert result.data["launch_request_accepted"] is True
    assert result.data["visible_effect_verified"] is False


def test_open_folder_executor_reports_rejected_when_os_launch_fails(monkeypatch, tmp_path: Path):
    executor = OpenFolderExecutor()
    target = tmp_path / "Documents"
    target.mkdir()

    monkeypatch.setattr(
        executor.system_control,
        "open_path_result",
        lambda path: _launch_result(OpenPathLaunchState.REJECTED, "path_not_allowed"),
    )
    result = executor.execute(ActionRequest(capability_id=22, params={"path": str(target)}))

    assert result.success is False
    assert "couldn't send" in result.message.lower()
    assert result.data["outcome_state"] == "rejected"
    assert result.data["launch_request_accepted"] is False
    assert result.data["visible_effect_verified"] is False


def test_open_folder_executor_preserves_launcher_reported_failure(monkeypatch, tmp_path: Path):
    executor = OpenFolderExecutor()
    target = tmp_path / "Documents"
    target.mkdir()

    monkeypatch.setattr(
        executor.system_control,
        "open_path_result",
        lambda path: _launch_result(
            OpenPathLaunchState.FAILED,
            "launcher_reported_failure",
            returncode=3,
        ),
    )
    result = executor.execute(ActionRequest(capability_id=22, params={"path": str(target)}))

    assert result.success is False
    assert result.status == "failed"
    assert "system launcher reported a failure" in result.message.lower()
    assert "couldn't verify" in result.message.lower()
    assert result.data["outcome_state"] == "failed"
    assert "launch_request_accepted" not in result.data
    assert result.data["visible_effect_verified"] is False
    assert result.data["launcher_returncode"] == 3


def test_open_folder_executor_preserves_unknown_post_dispatch_outcome(
    monkeypatch, tmp_path: Path
):
    executor = OpenFolderExecutor()
    target = tmp_path / "Documents"
    target.mkdir()

    monkeypatch.setattr(
        executor.system_control,
        "open_path_result",
        lambda path: _launch_result(
            OpenPathLaunchState.UNKNOWN,
            "launcher_timed_out_outcome_unknown",
        ),
    )
    result = executor.execute(ActionRequest(capability_id=22, params={"path": str(target)}))

    assert result.success is False
    assert result.status == "failed"
    assert "may have been dispatched" in result.message.lower()
    assert "couldn't verify" in result.message.lower()
    assert "rejected" not in result.message.lower()
    assert result.data["outcome_state"] == "unknown_unverified"
    assert "launch_request_accepted" not in result.data
    assert result.data["visible_effect_verified"] is False


def test_open_folder_executor_reports_opened_only_after_visible_verification(
    monkeypatch, tmp_path: Path
):
    executor = OpenFolderExecutor()
    target = tmp_path / "Downloads"
    target.mkdir()

    monkeypatch.setattr("src.executors.open_folder_executor.PRESET_FOLDERS", {"downloads": target})
    monkeypatch.setattr(
        executor.system_control,
        "open_path_result",
        lambda path: _launch_result(OpenPathLaunchState.ACCEPTED),
    )
    monkeypatch.setattr(executor, "_trusted_visible_explorer_paths", lambda: (target,))
    result = executor.execute(ActionRequest(capability_id=22, params={"target": "downloads"}))

    assert result.success is True
    assert result.message == f"Opened your downloads folder: {target}"
    assert result.data["outcome_state"] == "visible_verified"
    assert result.data["launch_request_accepted"] is True
    assert result.data["visible_effect_verified"] is True


def test_open_folder_executor_does_not_verify_same_title_for_different_path(
    monkeypatch, tmp_path: Path
):
    executor = OpenFolderExecutor()
    requested = tmp_path / "home" / "Downloads"
    unrelated = tmp_path / "archive" / "Downloads"
    requested.mkdir(parents=True)
    unrelated.mkdir(parents=True)

    monkeypatch.setattr(
        "src.executors.open_folder_executor.PRESET_FOLDERS",
        {"downloads": requested},
    )
    monkeypatch.setattr(
        executor.system_control,
        "open_path_result",
        lambda path: _launch_result(OpenPathLaunchState.ACCEPTED),
    )
    monkeypatch.setattr(
        executor,
        "_trusted_visible_explorer_paths",
        lambda: (unrelated,),
    )
    result = executor.execute(ActionRequest(capability_id=22, params={"target": "downloads"}))

    assert requested.name == unrelated.name
    assert result.success is True
    assert result.data["outcome_state"] == "accepted_unverified"
    assert result.data["launch_request_accepted"] is True
    assert result.data["visible_effect_verified"] is False
    assert "couldn't verify" in result.message.lower()
    assert "file manager" in result.message.lower()
    assert "File Explorer" not in result.message
    assert not result.message.lower().startswith("opened")
