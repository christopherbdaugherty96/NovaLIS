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
