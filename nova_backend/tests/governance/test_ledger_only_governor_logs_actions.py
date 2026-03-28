from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
GOVERNOR_PATH = SRC_ROOT / "governor" / "governor.py"
SKILLS_ROOT = SRC_ROOT / "skills"


ACTION_EVENTS = {"ACTION_ATTEMPTED", "ACTION_COMPLETED"}


def test_action_events_only_emitted_in_governor():
    offenders: list[str] = []

    for py in SRC_ROOT.rglob("*.py"):
        text = py.read_text(encoding="utf-8", errors="replace")
        for event_name in ACTION_EVENTS:
            token = f'log_event("{event_name}"'
            if token in text and py != GOVERNOR_PATH:
                offenders.append(f"{py}: contains {event_name}")

    assert not offenders, "\n".join(offenders)


def test_skills_do_not_emit_action_attempted_or_completed():
    offenders: list[str] = []

    for py in SKILLS_ROOT.rglob("*.py"):
        text = py.read_text(encoding="utf-8", errors="replace")
        for event_name in ACTION_EVENTS:
            if f'log_event("{event_name}"' in text:
                offenders.append(f"{py}: emits forbidden ledger event {event_name}")

    assert not offenders, "\n".join(offenders)
