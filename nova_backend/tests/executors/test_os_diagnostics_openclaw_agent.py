from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor


def test_connection_status_details_include_openclaw_home_agent():
    payload = OSDiagnosticsExecutor._connection_status_details()

    labels = [str(item.get("label") or "").strip() for item in payload.get("items") or []]

    assert "Home agent foundation" in labels
    assert "Agent delivery model" in labels
    assert "Agent scheduler" in labels
    assert "OpenAI metered lane" in labels
    assert "AI routing mode" in labels
    assert "agent_runtime" in payload
    assert "openai_runtime" in payload


def test_external_reasoning_status_details_include_latest_review_summary_fields(tmp_path, monkeypatch):
    from src.ledger import writer as ledger_writer

    ledger_path = tmp_path / "ledger.jsonl"
    ledger_path.write_text(
        (
            '{"timestamp_utc":"2026-03-28T10:00:00+00:00","event_type":"ACTION_COMPLETED",'
            '"capability_id":62,"success":true,"request_id":"req-77",'
            '"reasoning_provider_label":"DeepSeek","reasoning_route_label":"Governed second-opinion lane",'
            '"reasoning_mode":"second_opinion","reasoning_summary_line":"Bottom line: The review partly agrees.",'
            '"top_issue":"one caveat is missing","top_correction":"add the missing caveat"}\n'
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(ledger_writer, "LEDGER_PATH", str(ledger_path))

    payload = OSDiagnosticsExecutor._external_reasoning_status_details()

    assert payload["reasoning_summary_line"] == "Bottom line: The review partly agrees."
    assert payload["top_issue"] == "one caveat is missing"
    assert payload["top_correction"] == "add the missing caveat"
