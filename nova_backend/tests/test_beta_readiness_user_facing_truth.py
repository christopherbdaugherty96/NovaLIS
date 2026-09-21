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
    ):
        assert (STATIC / name).read_bytes() == (MIRROR / name).read_bytes()
