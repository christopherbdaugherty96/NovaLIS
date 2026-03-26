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


def test_render_current_runtime_state_uses_phase5_package_note():
    import src.audit.runtime_auditor as ra

    registry = {
        "capabilities": [
            {"id": 61, "name": "memory_governance", "enabled": True, "status": "active"},
        ]
    }

    rendered = ra.render_current_runtime_state_markdown({"discrepancies": []}, registry)

    assert "Governed memory, continuity, tone, scheduling, and pattern-review surfaces active" in rendered
    assert "full closure remains gated" not in rendered


def test_phase6_status_tracks_complete_review_surface(monkeypatch, tmp_path):
    import src.audit.runtime_auditor as ra

    atomic_store = tmp_path / "atomic_policy_store.py"
    policy_validator = tmp_path / "policy_validator.py"
    policy_gate = tmp_path / "policy_executor_gate.py"
    capability_topology = tmp_path / "capability_topology.py"
    for path in (atomic_store, policy_validator, policy_gate, capability_topology):
        path.write_text("# present\n", encoding="utf-8")

    monkeypatch.setattr(ra, "ATOMIC_POLICY_STORE_PATH", atomic_store)
    monkeypatch.setattr(ra, "POLICY_VALIDATOR_PATH", policy_validator)
    monkeypatch.setattr(ra, "POLICY_EXECUTOR_GATE_PATH", policy_gate)
    monkeypatch.setattr(ra, "CAPABILITY_TOPOLOGY_PATH", capability_topology)

    contents = {
        ra.STATIC_DASHBOARD_PATH: "\n".join(
            [
                "function renderPolicyCenterPage() {}",
                "function renderTrustCenterPage() {}",
                'case "policy_overview":',
                'case "policy_run":',
                "let trustReviewState = { selectedPolicyCapabilityKey: '' };",
                "function getPolicyReadinessBuckets(snapshot = {}) {}",
            ]
        ),
        ra.STATIC_INDEX_PATH: "\n".join(
            [
                '<div id="page-policy"></div>',
                '<div id="page-trust"></div>',
                '<div id="trust-center-policy-summary"></div>',
                '<div id="policy-center-readiness"></div>',
                '<button id="btn-policy-capability-map"></button>',
            ]
        ),
        ra.BRAIN_SERVER_PATH: "\n".join(
            [
                "policy overview",
                "policy simulate <id>",
                "policy run <id> once",
                "policy_capability_readiness",
                "POLICY_CAPABILITY_MAP_COMMANDS",
                "POLICY_CAPABILITY_MAP_VIEWED",
            ]
        ),
    }
    monkeypatch.setattr(ra, "_safe_read", lambda path: contents.get(path, ""))

    assert ra._phase_6_status() == "COMPLETE"


def test_governance_rows_prefer_explicit_registry_authority_metadata():
    import src.audit.runtime_auditor as ra

    registry = {
        "capabilities": [
            {
                "id": 22,
                "name": "open_file_folder",
                "enabled": True,
                "status": "active",
                "phase_introduced": "4",
                "risk_level": "confirm",
                "data_exfiltration": False,
                "authority_class": "reversible_local",
                "requires_confirmation": True,
                "reversible": True,
                "external_effect": False,
            }
        ]
    }

    rows = ra._derive_capability_governance_rows(registry)

    assert rows[0]["authority_class"] == "reversible_local"
    assert rows[0]["confirmation_required"] is True
    assert rows[0]["reversible"] is True
    assert rows[0]["external_effect"] is False


def test_runtime_surface_hash_ignores_line_ending_only_differences(monkeypatch, tmp_path):
    import src.audit.runtime_auditor as ra

    runtime_dir = tmp_path / "docs" / "current_runtime"
    runtime_dir.mkdir(parents=True)
    sample = tmp_path / "nova_backend" / "src" / "executors" / "sample_executor.py"
    sample.parent.mkdir(parents=True)

    monkeypatch.setattr(ra, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(ra, "RUNTIME_DOC_DIR", runtime_dir)
    monkeypatch.setattr(ra, "ALLOWED_READ_PATHS", {sample})

    sample.write_bytes(b"line one\r\nline two\r\n")
    crlf_hash = ra._runtime_surface_hash()

    sample.write_bytes(b"line one\nline two\n")
    lf_hash = ra._runtime_surface_hash()

    assert crlf_hash == lf_hash
