from src.audit.runtime_auditor import _build_discrepancies, _derive_status


def test_status_warn_tier_when_only_warnings():
    assert _derive_status(hard_fail_count=0, warning_count=2) == "warn"


def test_status_fail_overrides_warnings():
    assert _derive_status(hard_fail_count=1, warning_count=3) == "fail"


def test_mediator_vs_enabled_mismatch_detection_and_execution_gate_warning():
    discrepancies = _build_discrepancies(
        runtime_doc_enabled_ids=[16, 17],
        registry_enabled_ids=[16, 17],
        mediator_mapped_ids=[16, 17, 22],
        model_path_signals={"deepseek_uses_ollama_chat_directly": False},
        execution_gate_enabled=False,
    )

    codes = {item.code for item in discrepancies}
    assert "MEDIATOR_ROUTES_TO_DISABLED_CAPABILITY" in codes
    assert "EXECUTION_GATE_DISABLED" in codes


def test_enabled_id_extraction_ignores_non_enabled_truthy_columns():
    markdown = """
## Capability table
| id | name | enabled | status | risk_level | data_exfiltration |
| --- | --- | --- | --- | --- | --- |
| 16 | a | True | active | low | True |
| 48 | b | False | active | low | True |
## Runtime truth discrepancies
"""
    from src.audit.runtime_auditor import _extract_enabled_ids_from_markdown

    assert _extract_enabled_ids_from_markdown(markdown) == [16]


def test_missing_enabled_mediator_route_is_hard_fail():
    discrepancies = _build_discrepancies(
        runtime_doc_enabled_ids=[16, 17],
        registry_enabled_ids=[16, 17, 18],
        mediator_mapped_ids=[16, 17],
        model_path_signals={"deepseek_uses_ollama_chat_directly": False},
        execution_gate_enabled=True,
    )

    missing = [d for d in discrepancies if d.code == "ENABLED_CAPABILITY_MISSING_MEDIATOR_ROUTE"]
    assert missing
    assert missing[0].severity == "hard_fail"


def test_calendar_detector_matches_live_runtime_path(monkeypatch):
    import src.audit.runtime_auditor as ra
    from src.governor.governor_mediator import Invocation

    contents = {
        ra.SKILL_REGISTRY_PATH: "from src.skills.calendar import CalendarSkill\nskills = [CalendarSkill()]",
        ra.GOVERNOR_PATH: "elif req.capability_id == 57:\n    return self._handle_calendar(req)",
        ra.BRAIN_SERVER_PATH: 'session_state["last_calendar_summary"] = ""\nawait send_widget_message(ws, "calendar", message, widget)',
        ra.STATIC_DASHBOARD_PATH: 'case "calendar":\nmorningState.calendar = payload;',
        ra.STATIC_INDEX_PATH: '<section id="morning-calendar"></section>',
    }

    monkeypatch.setattr(ra, "_safe_read", lambda path: contents.get(path, ""))
    monkeypatch.setattr(
        ra.GovernorMediator,
        "parse_governed_invocation",
        lambda text, session_id=None: Invocation(capability_id=57, params={}) if text == "calendar" else None,
    )

    assert ra._calendar_integration_present() is True


def test_phase5_status_tracks_active_runtime_slice():
    import src.audit.runtime_auditor as ra

    registry = {
        "capabilities": [
            {"id": 61, "name": "memory_governance", "enabled": True, "status": "active"},
        ]
    }

    assert ra._phase_5_status(registry) == "ACTIVE"
