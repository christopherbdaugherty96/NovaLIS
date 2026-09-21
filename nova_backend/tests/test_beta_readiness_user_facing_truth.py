from pathlib import Path

from src.conversation.meta_intent_handler import MetaIntentHandler


ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "nova_backend" / "static"
MIRROR = ROOT / "Nova-Frontend-Dashboard"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def test_beta_ui_does_not_advertise_unproven_live_or_builder_claims():
    index = _read(STATIC / "index.html")
    config = _read(STATIC / "dashboard-config.js")
    control = _read(STATIC / "dashboard-control-center.js")
    visible_truth = "\n".join((index, config, control))

    for banned in (
        "build me a landing page for my business",
        "Nova finished the current step",
        "Live Screen Help",
        "Start live help",
        'Say "Hey Nova"',
    ):
        assert banned not in visible_truth

    assert 'id="live-help-widget"' not in index
    assert 'id="btn-live-help-start"' not in index


def test_generic_suggestions_exclude_context_and_configuration_only_actions():
    config = _read(STATIC / "dashboard-config.js")

    for context_only in (
        "which one should I download",
        "why this recommendation",
        "continue where I left off",
        "what was I working on",
        "which project needs attention",
        "what are my biggest blockers",
    ):
        assert context_only not in config

    for conditional in (
        "show my schedule",
        "check my calendar",
        '"volume up"',
        '"brightness down"',
        '"set volume 40"',
        '"set brightness 50"',
    ):
        assert conditional not in config

    assert 'label: "Draft calendar rule"' in config
    assert 'label: "Draft weather rule"' in config
    assert 'label: "Create calendar rule"' not in config
    assert 'label: "Create weather rule"' not in config


def test_workflow_narration_stays_response_scoped_not_outcome_scoped():
    control = _read(STATIC / "dashboard-control-center.js")

    assert "Nova returned a response for the current request." in control
    assert "Response received." in control
    assert "Nova finished the current step" not in control
    assert "Turning your idea into a build plan" not in control
    assert "Planning what would be needed" in control


def test_capability_help_describes_local_first_and_bounded_controls():
    response = MetaIntentHandler().handle("who are you", session_state={"turn_count": 1})

    assert response is not None
    lowered = response.lower()
    assert "local-first" in lowered
    assert "external/network paths are explicit, governed, and visible when used" in lowered
    assert "bounded local controls" in lowered
    assert "everything runs on your machine" not in lowered
    assert "control parts of your computer" not in lowered


def test_frontend_truth_surfaces_remain_byte_synced():
    for name in (
        "index.html",
        "dashboard-config.js",
        "dashboard-control-center.js",
        "dashboard-chat-news.js",
        "dashboard-workspace.js",
        "dashboard.js",
    ):
        assert (STATIC / name).read_bytes() == (MIRROR / name).read_bytes()

def test_page_quick_actions_use_runtime_availability_gating():
    chat_news = _read(STATIC / "dashboard-chat-news.js")

    assert "getQuickActionsForPage(page).filter((action) => isUserFacingSuggestionAvailable(action.command))" in chat_news
    assert 'return isConnectedSuggestionProvider("brave")' in chat_news
    assert 'return isConnectedSuggestionProvider("news")' in chat_news
    assert 'return isConnectedSuggestionProvider("calendar")' in chat_news
    assert "return hasProjectSuggestionContext()" in chat_news


def test_current_focus_only_changes_for_a_manual_request_response():
    control = _read(STATIC / "dashboard-control-center.js")

    assert 'if (!clean || !workflowFocusState.awaitingResponse) return;' in control
    assert 'workflowFocusState.status = "Response ready";' in control
    assert 'workflowFocusState.status = "Ready for review";' not in control


def test_disconnected_news_and_home_copy_do_not_claim_live_or_connected_work():
    index = _read(STATIC / "index.html")

    assert ">Live briefing<" not in index
    assert ">Briefing<" in index
    assert "Nova will show starting points that are available on this device and its connected services." in index


def test_remote_bridge_separates_permission_from_runtime_availability():
    control = _read(STATIC / "dashboard-control-center.js")

    assert '["Permission", permissionEnabled ? "Enabled" : "Paused"]' in control
    assert '["Availability", availabilityLabel]' in control
    assert '"Unavailable — token not configured"' in control
    assert '["Remote permission", setup.remote_bridge_enabled ? "Enabled" : "Paused"]' in control
    assert '["Remote availability", setup.remote_bridge_enabled && setup.remote_bridge_token_configured' in control


def test_home_filters_internal_paths_and_stale_dated_watch_copy():
    workspace = _read(STATIC / "dashboard-workspace.js")

    assert 'text.includes("local_project_structure_map")' in workspace
    assert 'text.includes("c:\\\\nova-project")' in workspace
    assert "isStaleDatedWatch" in workspace
    assert "No current assistive notices." in workspace
    assert "userFacingSelectedFile" in workspace
    assert "hasProjectThreadContext ? String(snapshot.task_goal" in workspace
    assert "hasProjectThreadContext ? String(snapshot.current_step" in workspace


def test_settings_html_does_not_present_wake_word_as_live():
    index = _read(STATIC / "index.html")

    assert "Hey Nova" not in index
    assert "wake phrase" not in index.lower()
    assert "live screen help" not in index.lower()

