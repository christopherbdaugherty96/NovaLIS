"""Semantic contract: one user-facing Daily Brief.

The bug this protects against was not code duplication — it was semantic
drift between UI labels, the commands those labels send, and the route
those commands take. A button said "Morning brief" but sent "daily brief",
and "daily brief" routed to the Cap 50 news report instead of the governed
RoutineGraph brief.

Contract (UX_SIMPLIFICATION_PRIORITY_LOCK_2026-07-02.md, One Brief):
  1. Every UI action that sends a brief command is labeled "Daily brief"
     and sends "daily brief".
  2. Every user-facing brief phrasing resolves through the single trigger
     predicate to the governed Daily Brief path.
  3. The mediator does not capture "daily brief" into another capability.
  4. The session handler uses the shared predicate — no inline trigger sets.
  5. The frontend mirror is byte-identical to the served static bundle, so
     labels/commands cannot drift between the two trees.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from src.conversation.morning_brief_handler import is_daily_brief_request
from src.governor.governor_mediator import GovernorMediator

NOVA_BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = NOVA_BACKEND_ROOT.parent
STATIC_ROOT = NOVA_BACKEND_ROOT / "static"
MIRROR_ROOT = REPO_ROOT / "Nova-Frontend-Dashboard"

CONFIG_SRC = (STATIC_ROOT / "dashboard-config.js").read_text(encoding="utf-8")
DASHBOARD_SRC = (STATIC_ROOT / "dashboard.js").read_text(encoding="utf-8")
SESSION_HANDLER_SRC = (
    NOVA_BACKEND_ROOT / "src" / "websocket" / "session_handler.py"
).read_text(encoding="utf-8")

_ACTION_RE = re.compile(r'\{\s*id:\s*"[^"]+",\s*label:\s*"(?P<label>[^"]+)",[^}]*?command:\s*"(?P<command>[^"]+)"')


def _quick_actions() -> list[tuple[str, str]]:
    return [(m.group("label"), m.group("command")) for m in _ACTION_RE.finditer(CONFIG_SRC)]


class TestUiLabelCommandContract:
    def test_quick_actions_parsed(self):
        actions = _quick_actions()
        assert len(actions) > 10, "quick-action parser found too few entries"

    def test_every_daily_brief_command_labeled_daily_brief(self):
        for label, command in _quick_actions():
            if command == "daily brief":
                assert label == "Daily brief", (
                    f"Action labeled {label!r} sends 'daily brief' — label and "
                    "command must agree (one user-facing Daily Brief)"
                )

    def test_every_daily_brief_label_sends_daily_brief(self):
        for label, command in _quick_actions():
            if label.lower() == "daily brief":
                assert command == "daily brief", (
                    f"Action labeled 'Daily brief' sends {command!r}"
                )

    def test_no_ui_surface_sends_or_shows_morning_brief(self):
        for name in ("dashboard-config.js", "dashboard.js", "dashboard-chat-news.js"):
            src = (STATIC_ROOT / name).read_text(encoding="utf-8")
            assert not re.search(r"morning brief", src, re.IGNORECASE), (
                f"{name} still references 'morning brief' — the user-facing "
                "name is Daily Brief"
            )

    def test_first_run_prompt_is_a_daily_brief_trigger(self):
        m = re.search(r'FIRST_RUN_DEFAULT_PROMPT:\s*"([^"]+)"', CONFIG_SRC)
        assert m, "FIRST_RUN_DEFAULT_PROMPT not found"
        assert is_daily_brief_request(m.group(1)), (
            "The first-run prompt must route to the governed Daily Brief"
        )


class TestPhraseRoutingContract:
    @pytest.mark.parametrize("phrase", [
        "daily brief",          # UI command + typed
        "morning brief",        # legacy typed phrase
        "what matters today",   # natural phrasing
        "brief me",
        "plan my day",          # former button label
        "catch me up",
    ])
    def test_phrase_resolves_to_daily_brief_path(self, phrase: str):
        assert is_daily_brief_request(phrase) is True

    def test_mediator_does_not_capture_daily_brief(self):
        # The session-level governed RoutineGraph path owns "daily brief".
        # If the mediator parses it into a capability, typed input and UI
        # buttons would diverge from the Daily Brief again.
        assert GovernorMediator.parse_governed_invocation("daily brief") is None


class TestSessionHandlerUsesSharedPredicate:
    def test_session_handler_calls_predicate(self):
        assert "is_daily_brief_request(command_lowered)" in SESSION_HANDLER_SRC

    def test_daily_brief_precedes_domain_brief_resolution(self):
        predicate_line = SESSION_HANDLER_SRC.index(
            "governed_daily_brief_request = is_daily_brief_request(command_lowered)"
        )
        resolver_line = SESSION_HANDLER_SRC.index("brief_intent = resolve_brief_intent(")
        assert predicate_line < resolver_line
        assert "not governed_daily_brief_request" in SESSION_HANDLER_SRC[
            predicate_line:resolver_line
        ]

    def test_no_inline_brief_trigger_set(self):
        assert '"morning brief", "brief"' not in SESSION_HANDLER_SRC, (
            "Inline brief trigger set found — trigger truth lives in "
            "morning_brief_handler.DAILY_BRIEF_TRIGGERS only"
        )


class TestMirrorParity:
    @pytest.mark.parametrize("name", [
        "dashboard-config.js",
        "dashboard.js",
        "dashboard-chat-news.js",
        "dashboard-control-center.js",
        "dashboard-workspace.js",
        "dashboard-surfaces.css",
        "style.phase1.css",
        "index.html",
        "landing.html",
        "orb.js",
    ])
    def test_mirror_matches_static(self, name: str):
        static_file = STATIC_ROOT / name
        mirror_file = MIRROR_ROOT / name
        assert mirror_file.exists(), f"mirror missing {name}"
        assert static_file.read_bytes() == mirror_file.read_bytes(), (
            f"{name} differs between nova_backend/static and "
            "Nova-Frontend-Dashboard — sync the mirror in the same commit"
        )
