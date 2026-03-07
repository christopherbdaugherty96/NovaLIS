def test_open_folder_rejects_non_preset():
    from src.executors.open_folder_executor import OpenFolderExecutor
    from src.actions.action_request import ActionRequest

    ex = OpenFolderExecutor()
    req = ActionRequest(capability_id=22, params={"target": "../../secret"})
    result = ex.execute(req)

    assert result.success is False
    assert "preset folder" in result.message.lower()


def test_open_folder_accepts_explicit_path(tmp_path):
    from src.executors.open_folder_executor import OpenFolderExecutor
    from src.actions.action_request import ActionRequest

    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    ex = OpenFolderExecutor()
    ex.system_control.open_path = lambda p: True  # type: ignore[method-assign]
    req = ActionRequest(capability_id=22, params={"path": str(path)})
    result = ex.execute(req)

    assert result.success is True
    assert str(path) in result.message
