from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor


def test_ledger_status_uses_bounded_tail_reader(tmp_path, monkeypatch):
    from src.ledger import writer as ledger_writer

    ledger_path = tmp_path / "ledger.jsonl"
    ledger_path.write_text("placeholder\n", encoding="utf-8")
    monkeypatch.setattr(ledger_writer, "LEDGER_PATH", str(ledger_path))

    calls = {"count": 0}

    def _fake_tail(path):
        calls["count"] += 1
        assert path == ledger_path
        return [
            '{"timestamp_utc":"2026-07-09T23:59:00+00:00","event_type":"OLD_EVENT"}',
            '{"timestamp_utc":"2099-01-01T12:00:00+00:00","event_type":"ACTION_COMPLETED"}',
        ]

    monkeypatch.setattr(
        OSDiagnosticsExecutor,
        "_read_ledger_tail_lines",
        staticmethod(_fake_tail),
    )
    monkeypatch.setattr(
        "src.executors.os_diagnostics_executor.datetime",
        type(
            "_FixedDateTime",
            (),
            {
                "now": staticmethod(lambda tz=None: __import__("datetime").datetime(2099, 1, 1, tzinfo=tz)),
                "fromisoformat": staticmethod(__import__("datetime").datetime.fromisoformat),
            },
        ),
    )

    assert OSDiagnosticsExecutor._ledger_status_details() == ("ok", 1, "ACTION_COMPLETED")
    assert calls["count"] == 1


def test_recent_runtime_activity_uses_bounded_tail_reader(tmp_path, monkeypatch):
    from src.ledger import writer as ledger_writer

    ledger_path = tmp_path / "ledger.jsonl"
    ledger_path.write_text("placeholder\n", encoding="utf-8")
    monkeypatch.setattr(ledger_writer, "LEDGER_PATH", str(ledger_path))

    calls = {"count": 0}

    def _fake_tail(path):
        calls["count"] += 1
        assert path == ledger_path
        return [
            (
                0,
                '{"timestamp_utc":"2099-01-01T12:00:00+00:00","event_type":"ACTION_ATTEMPTED",'
                '"capability_id":32,"request_id":"req-1"}',
            ),
            (
                128,
                '{"timestamp_utc":"2099-01-01T12:01:00+00:00","event_type":"ACTION_COMPLETED",'
                '"capability_id":32,"success":true,"request_id":"req-1"}',
            ),
        ]

    monkeypatch.setattr(
        OSDiagnosticsExecutor,
        "_read_ledger_tail_records",
        staticmethod(_fake_tail),
    )

    items, summary = OSDiagnosticsExecutor._recent_runtime_activity(
        [{"id": 32, "name": "os_diagnostics"}],
        limit=1,
    )

    assert calls["count"] == 1
    assert len(items) == 1
    assert items[0]["event_type"] == "ACTION_COMPLETED"
    assert items[0]["ledger_ref"] == "B128"
    assert "latest 1" in summary


def test_recent_runtime_activity_accepts_a_deeper_bounded_scan_for_home(tmp_path, monkeypatch):
    from src.ledger import writer as ledger_writer

    ledger_path = tmp_path / "ledger.jsonl"
    ledger_path.write_text("placeholder\n", encoding="utf-8")
    monkeypatch.setattr(ledger_writer, "LEDGER_PATH", str(ledger_path))
    requested_limits: list[int] = []

    def _fake_tail(path, line_limit):
        assert path == ledger_path
        requested_limits.append(line_limit)
        return [
            (
                0,
                '{"timestamp_utc":"2099-01-01T12:01:00+00:00",'
                '"event_type":"MODEL_NETWORK_CALL"}',
            )
        ]

    monkeypatch.setattr(
        OSDiagnosticsExecutor,
        "_read_ledger_tail_records",
        staticmethod(_fake_tail),
    )

    items, _summary = OSDiagnosticsExecutor._recent_runtime_activity(
        [],
        limit=1,
        scan_line_limit=5000,
    )

    assert requested_limits == [5000]
    assert len(items) == 1


def test_recent_runtime_activity_preserves_byte_offset_ledger_ref(tmp_path, monkeypatch):
    from src.ledger import writer as ledger_writer

    ledger_path = tmp_path / "ledger.jsonl"
    first = (
        '{"timestamp_utc":"2099-01-01T12:00:00+00:00","event_type":"ACTION_ATTEMPTED",'
        '"capability_id":32,"request_id":"req-1"}\n'
    )
    second = (
        '{"timestamp_utc":"2099-01-01T12:01:00+00:00","event_type":"ACTION_COMPLETED",'
        '"capability_id":32,"success":true,"request_id":"req-1"}\n'
    )
    ledger_path.write_bytes((first + second).encode("utf-8"))
    monkeypatch.setattr(ledger_writer, "LEDGER_PATH", str(ledger_path))

    items, _summary = OSDiagnosticsExecutor._recent_runtime_activity(
        [{"id": 32, "name": "os_diagnostics"}],
        limit=1,
    )

    assert len(items) == 1
    assert items[0]["event_type"] == "ACTION_COMPLETED"
    assert items[0]["ledger_ref"] == f"B{len(first.encode('utf-8'))}"


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
