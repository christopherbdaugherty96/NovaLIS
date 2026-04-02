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


def test_requests_detector_ignores_plain_language_mentions(monkeypatch, tmp_path):
    import src.audit.runtime_auditor as ra

    brain_path = tmp_path / "brain_server.py"
    brain_path.write_text('detail = "Remote requests stay blocked until enabled."\n', encoding="utf-8")

    allowed = frozenset({brain_path})
    monkeypatch.setattr(ra, "ALLOWED_READ_PATHS", allowed)
    monkeypatch.setattr(ra, "PROJECT_ROOT", tmp_path)

    assert ra._find_requests_usage_outside_network_mediator() == []


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


def test_render_current_runtime_state_mentions_remote_bridge_when_present(monkeypatch):
    import src.audit.runtime_auditor as ra

    registry = {"capabilities": []}
    original_safe_read = ra._safe_read

    def _fake_safe_read(path):
        if path == ra.BRAIN_SERVER_PATH:
            return "build_bridge_router"
        if path == ra.BRIDGE_API_PATH:
            return '"/api/openclaw/bridge/message"\nopenclaw_bridge'
        return original_safe_read(path)

    monkeypatch.setattr(ra, "_safe_read", _fake_safe_read)

    rendered = ra.render_current_runtime_state_markdown({"discrepancies": []}, registry)

    assert "Governed Remote Bridge" in rendered
    assert "Token-gated read/reasoning ingress active" in rendered


def test_render_current_runtime_state_mentions_openclaw_home_agent_foundation(monkeypatch, tmp_path):
    import src.audit.runtime_auditor as ra

    registry = {"capabilities": []}
    original_safe_read = ra._safe_read
    agent_api_path = tmp_path / "openclaw_agent_api.py"
    runner_path = tmp_path / "agent_runner.py"
    store_path = tmp_path / "agent_runtime_store.py"
    personality_bridge_path = tmp_path / "agent_personality_bridge.py"
    for path in (agent_api_path, runner_path, store_path, personality_bridge_path):
        path.write_text("# present\n", encoding="utf-8")

    monkeypatch.setattr(ra, "OPENCLAW_AGENT_API_PATH", agent_api_path)
    monkeypatch.setattr(ra, "OPENCLAW_AGENT_RUNNER_PATH", runner_path)
    monkeypatch.setattr(ra, "OPENCLAW_AGENT_RUNTIME_STORE_PATH", store_path)
    monkeypatch.setattr(ra, "OPENCLAW_AGENT_PERSONALITY_BRIDGE_PATH", personality_bridge_path)

    def _fake_safe_read(path):
        if path == ra.STATIC_INDEX_PATH:
            return '<section id="page-agent"></section>'
        if path == ra.STATIC_DASHBOARD_PATH:
            return "function renderOpenClawAgentPage() {}"
        if path == ra.OPENCLAW_AGENT_API_PATH:
            return '"/api/openclaw/agent/status"\nhome_agent_enabled'
        if path == ra.OPENCLAW_AGENT_RUNTIME_STORE_PATH:
            return path.read_text(encoding="utf-8")
        return original_safe_read(path)

    monkeypatch.setattr(ra, "_safe_read", _fake_safe_read)

    rendered = ra.render_current_runtime_state_markdown({"discrepancies": []}, registry)

    assert "OpenClaw Home Agent Foundation" in rendered
    assert "Manual briefing templates, delivery controls, and operator surface active" in rendered


def test_render_current_runtime_state_mentions_connector_package_foundation(monkeypatch):
    import src.audit.runtime_auditor as ra

    registry = {"capabilities": []}
    monkeypatch.setattr(
        ra,
        "_connector_package_foundation_summary",
        lambda: {"present": True, "active_count": 2, "package_ids": ["ics_calendar", "rss_news"]},
    )

    rendered = ra.render_current_runtime_state_markdown({"discrepancies": []}, registry)

    assert "Governed Connector Package Foundation" in rendered
    assert "2 active package manifests" in rendered
    assert "ics_calendar, rss_news" in rendered


def test_phase8_status_tracks_foundation_slice(monkeypatch, tmp_path):
    import src.audit.runtime_auditor as ra

    openclaw_dir = tmp_path / "openclaw"
    openclaw_dir.mkdir()
    scheduler_path = tmp_path / "agent_scheduler.py"

    monkeypatch.setattr(ra, "OPENCLAW_DIR", openclaw_dir)
    monkeypatch.setattr(ra, "OPENCLAW_AGENT_SCHEDULER_PATH", scheduler_path)
    monkeypatch.setattr(ra, "_openclaw_home_agent_foundation_present", lambda: True)

    assert ra._phase_8_status() == "FOUNDATION"


def test_phase8_status_tracks_active_scheduler_slice(monkeypatch, tmp_path):
    import src.audit.runtime_auditor as ra

    scheduler_path = tmp_path / "agent_scheduler.py"
    scheduler_path.write_text("# present\n", encoding="utf-8")

    monkeypatch.setattr(ra, "OPENCLAW_AGENT_SCHEDULER_PATH", scheduler_path)
    monkeypatch.setattr(ra, "_openclaw_home_agent_foundation_present", lambda: True)

    assert ra._phase_8_status() == "ACTIVE"


def test_render_current_runtime_state_includes_phase8_foundation_row(monkeypatch):
    import src.audit.runtime_auditor as ra

    registry = {"capabilities": []}
    monkeypatch.setattr(ra, "_phase_8_status", lambda: "FOUNDATION")

    rendered = ra.render_current_runtime_state_markdown({"discrepancies": []}, registry)

    assert "| Phase 8 | FOUNDATION |" in rendered
    assert "scheduled automation and full Phase-8 execution enforcement remain deferred" in rendered


def test_render_current_runtime_state_includes_phase8_active_row(monkeypatch):
    import src.audit.runtime_auditor as ra

    registry = {"capabilities": []}
    monkeypatch.setattr(ra, "_phase_8_status", lambda: "ACTIVE")

    rendered = ra.render_current_runtime_state_markdown({"discrepancies": []}, registry)

    assert "| Phase 8 | ACTIVE |" in rendered
    assert "Scheduled home-agent runtime is available behind explicit settings control" in rendered


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


def test_phase7_status_tracks_complete_reasoning_surface(monkeypatch, tmp_path):
    import src.audit.runtime_auditor as ra

    executor_path = tmp_path / "external_reasoning_executor.py"
    wrapper_path = tmp_path / "deepseek_safety_wrapper.py"
    settings_api_path = tmp_path / "settings_api.py"
    executor_path.write_text("# present\n", encoding="utf-8")
    wrapper_path.write_text("# present\n", encoding="utf-8")
    settings_api_path.write_text('@router.get("/api/settings/runtime")\n', encoding="utf-8")

    monkeypatch.setattr(ra, "EXTERNAL_REASONING_EXECUTOR_PATH", executor_path)
    monkeypatch.setattr(ra, "DEEPSEEK_SAFETY_WRAPPER_PATH", wrapper_path)
    monkeypatch.setattr(ra, "SETTINGS_API_PATH", settings_api_path)
    monkeypatch.setattr(ra, "BUILD_PHASE", 7)

    registry = {
        "capabilities": [
            {"id": 62, "name": "external_reasoning_review", "enabled": True, "status": "active"},
        ]
    }

    contents = {
        ra.STATIC_DASHBOARD_PATH: "\n".join(
            [
                "trustReviewState.reasoningRuntime = {};",
                "trust-center-reasoning-summary",
                "settings-reasoning-summary",
                "requestSettingsRuntimeRefresh(force = false)",
                "setRuntimePermission(permission, enabled)",
            ]
        ),
        ra.STATIC_INDEX_PATH: "\n".join(
            [
                '<div id="trust-center-reasoning-summary"></div>',
                '<div id="trust-center-reasoning-grid"></div>',
                '<div id="settings-reasoning-summary"></div>',
                '<div id="settings-reasoning-grid"></div>',
                '<div id="settings-permission-summary"></div>',
                '<div id="settings-permission-grid"></div>',
            ]
        ),
        ra.GOVERNOR_PATH: "elif req.capability_id == 62:\n    return self._handle_external_reasoning(req)",
        ra.GOVERNOR_MEDIATOR_PATH: "SECOND_OPINION_RE = re.compile('second opinion')",
        ra.BRAIN_SERVER_PATH: "\n".join(
            [
                "capability_id == 62",
                "_build_second_opinion_review_text",
                "reasoning_runtime",
                "build_settings_router",
            ]
        ),
        ra.SETTINGS_API_PATH: '@router.get("/api/settings/runtime")',
        ra.DEEPSEEK_BRIDGE_PATH: "response = llm_gateway.generate_chat(prompt)",
    }
    monkeypatch.setattr(ra, "_safe_read", lambda path: contents.get(path, ""))

    assert ra._phase_7_status(registry) == "COMPLETE"


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
