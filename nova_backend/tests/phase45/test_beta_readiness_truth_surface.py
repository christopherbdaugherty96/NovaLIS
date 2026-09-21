from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STATIC_ROOT = PROJECT_ROOT / "nova_backend" / "static"
MIRROR_ROOT = PROJECT_ROOT / "Nova-Frontend-Dashboard"
META_INTENT_PATH = (
    PROJECT_ROOT / "nova_backend" / "src" / "conversation" / "meta_intent_handler.py"
)

CHANGED_FRONTEND_FILES = (
    "index.html",
    "dashboard-config.js",
    "dashboard.js",
    "dashboard-control-center.js",
    "dashboard-chat-news.js",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _config_array(source: str, name: str, next_name: str) -> str:
    match = re.search(
        rf"{re.escape(name)}:\s*\[(.*?)\],\s*{re.escape(next_name)}:",
        source,
        re.S,
    )
    assert match, f"{name} block not found"
    return match.group(1)


def _function_block(source: str, name: str, next_name: str) -> str:
    start = source.index(f"function {name}")
    end = source.index(f"function {next_name}", start)
    return source[start:end]


def test_unproven_beta_claims_are_absent_from_primary_presentation() -> None:
    html = _read(STATIC_ROOT / "index.html")
    config = _read(STATIC_ROOT / "dashboard-config.js")
    dashboard = _read(STATIC_ROOT / "dashboard.js")
    control = _read(STATIC_ROOT / "dashboard-control-center.js")
    chat = _read(STATIC_ROOT / "dashboard-chat-news.js")

    for source in (html, config, dashboard, control, chat):
        assert "build me a landing page for my business" not in source.lower()
        assert "Nova finished the current step" not in source

    assert 'id="live-help-widget"' not in html
    assert "Start live help" not in html
    assert "Hey Nova" not in html
    assert "wake phrase" not in html.lower()
    assert '"What should I click?"' not in dashboard

    assert "Wake word available:" not in control
    assert "available for live help" not in control

    ptt = _function_block(dashboard, "setPTTButtonState", "flashPTTError")
    assert "HEY_NOVA_WAKE_WORD" not in ptt
    assert "live help" not in ptt.lower()
    assert "Press to record a short voice question." in ptt
    assert "Nova is listening. Press again to stop." in ptt

    privacy = _function_block(chat, "refreshPrivacyPanel", "showPrivacyModal")
    assert "HEY_NOVA_WAKE_WORD" not in privacy
    assert "wake word" not in privacy.lower()


def test_global_suggestions_do_not_advertise_context_or_device_only_actions() -> None:
    config = _read(STATIC_ROOT / "dashboard-config.js")
    commands = _config_array(config, "COMMAND_SUGGESTIONS", "HELP_EXAMPLES")
    examples = _config_array(config, "HELP_EXAMPLES", "COMMAND_DISCOVERY_GROUPS")
    global_copy = f"{commands}\n{examples}".lower()

    context_only = (
        "why this recommendation",
        "which one should i download",
        "continue where i left off",
        "what was i working on",
        "which project needs attention",
        "what are my biggest blockers",
    )
    configuration_or_device_only = (
        "show my schedule",
        "check my calendar",
        "volume up",
        "brightness down",
        '"play"',
        '"pause"',
    )

    for phrase in (*context_only, *configuration_or_device_only):
        assert phrase not in global_copy


def test_calendar_quick_action_requires_a_connected_calendar() -> None:
    config = _read(STATIC_ROOT / "dashboard-config.js")
    control = _read(STATIC_ROOT / "dashboard-control-center.js")

    assert (
        '{ id: "home_calendar", label: "Today\'s schedule", command: "calendar", '
        'switchToPage: "chat", requires: "calendar_connected" }'
    ) in config
    assert 'requirement === "calendar_connected"' in control
    assert 'getConnectionCardProvider("calendar")' in control
    assert "return actions.filter((action) => isQuickActionAvailable(action));" in control


def test_policy_controls_are_explicitly_draft_and_manual_only() -> None:
    html = _read(STATIC_ROOT / "index.html")
    config = _read(STATIC_ROOT / "dashboard-config.js")

    assert ">Draft calendar rule<" in html
    assert ">Draft weather rule<" in html
    assert ">Draft system-status rule<" in html
    assert ">Create calendar rule<" not in html
    assert ">Create weather rule<" not in html
    assert ">Create system-status rule<" not in html

    assert 'label: "Draft calendar rule"' in config
    assert 'label: "Draft weather rule"' in config
    assert "These rule drafts stay off until you review them." in html
    assert "One-time reviewed runs stay manual" in html


def test_planning_and_response_status_do_not_claim_verified_outcomes() -> None:
    dashboard = _read(STATIC_ROOT / "dashboard.js")
    control = _read(STATIC_ROOT / "dashboard-control-center.js")
    runtime = f"{dashboard}\n{control}"

    assert "Planning suggestions do not execute anything." in runtime
    assert 'workflowFocusState.status = "Response ready";' in control
    assert (
        "Nova returned a response. Review it before treating any suggested step as complete."
        in control
    )
    assert "Nova finished the current step" not in runtime
    assert "Nothing new was executed by the failed step" not in runtime


def test_capability_help_describes_local_first_and_bounded_controls() -> None:
    source = _read(META_INTENT_PATH)

    assert "Everything runs on your machine" not in source
    assert "control parts of your computer" not in source
    assert "local-first personal AI assistant" in source
    assert "network and cloud/model paths are explicit, governed, and visible when used" in source
    assert "bounded local controls" in source
    assert "prepare email drafts for manual sending" in source


def test_changed_frontend_files_remain_byte_synced_with_mirror() -> None:
    for name in CHANGED_FRONTEND_FILES:
        canonical = STATIC_ROOT / name
        mirror = MIRROR_ROOT / name
        assert canonical.read_bytes() == mirror.read_bytes(), (
            f"{name} differs between nova_backend/static and Nova-Frontend-Dashboard"
        )
