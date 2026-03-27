from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor


def test_connection_status_details_include_openclaw_home_agent():
    payload = OSDiagnosticsExecutor._connection_status_details()

    labels = [str(item.get("label") or "").strip() for item in payload.get("items") or []]

    assert "Home agent foundation" in labels
    assert "Agent delivery model" in labels
    assert "Agent scheduler" in labels
    assert "agent_runtime" in payload
