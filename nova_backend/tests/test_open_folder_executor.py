def test_open_folder_rejects_non_preset():
    from src.executors.open_folder_executor import OpenFolderExecutor
    from src.actions.action_request import ActionRequest

    ex = OpenFolderExecutor()
    req = ActionRequest(capability_id=22, params={"target": "../../secret"})
    result = ex.execute(req)

    assert result.success is False
    assert "preset folder" in result.message.lower()
