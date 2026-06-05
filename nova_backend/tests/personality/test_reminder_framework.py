"""Phase 2 — ReminderFramework tests.

Written before implementation. Proves:
  - ReminderFramework suggests reminders (plain dicts)
  - Pattern-derived reminders include opt-out
  - No governance, store, or client imports
  - No capability invocations, no persistence, no calendar creation
  - Only governed callers can persist reminders later
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Reminder creation
# ---------------------------------------------------------------------------

class TestReminderCreation:

    def test_reminder_framework_builds_session_reminder_suggestion(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.create_reminder("Call the electrician")
        assert reminder.text == "Call the electrician"
        assert reminder.source == "user_created"
        assert reminder.dismissed is False
        assert reminder.opt_out is False

    def test_reminder_framework_builds_project_reminder_suggestion(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.create_reminder(
            "Review the Shopify integration PR",
            source="user_created",
        )
        assert "Shopify" in reminder.text or "PR" in reminder.text
        assert reminder.source == "user_created"

    def test_reminder_framework_builds_business_reminder_suggestion(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.create_reminder("Follow up on Q3 invoice")
        assert reminder.text == "Follow up on Q3 invoice"
        assert isinstance(reminder.id, str)
        assert len(reminder.id) > 0

    def test_reminder_framework_pattern_derived(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.derive_from_pattern(
            "You mentioned calling the electrician twice this week",
            source_label="Session context",
        )
        assert reminder is not None
        assert reminder.source == "pattern_derived"

    def test_reminder_framework_pattern_derived_empty_returns_none(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.derive_from_pattern("", source_label="test")
        assert reminder is None


# ---------------------------------------------------------------------------
# Opt-out
# ---------------------------------------------------------------------------

class TestReminderOptOut:

    def test_reminder_framework_adds_opt_out_for_pattern_reminders(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.derive_from_pattern(
            "Repeated mention of calling the electrician",
            source_label="Memory",
        )
        assert reminder is not None
        notice = fw.to_notice(reminder)
        assert notice is not None
        summary_lower = notice["summary"].lower()
        actions_text = " ".join(
            a["command"].lower() for a in notice.get("suggested_actions", [])
        )
        has_opt_out = (
            "opt" in summary_lower
            or "stop" in summary_lower
            or "dismiss" in actions_text
        )
        assert has_opt_out, "Pattern reminder must include opt-out"

    def test_reminder_framework_user_created_no_forced_opt_out(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.create_reminder("Buy groceries")
        assert reminder.opt_out is False


# ---------------------------------------------------------------------------
# Output format
# ---------------------------------------------------------------------------

class TestReminderOutputFormat:

    def test_reminder_framework_output_is_plain_dict(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.create_reminder("Test reminder")
        notice = fw.to_notice(reminder)
        assert isinstance(notice, dict)
        # Must be JSON-serializable plain dict
        import json
        serialized = json.dumps(notice)
        assert isinstance(serialized, str)

    def test_reminder_framework_to_notice_returns_tier3_chat_input_only(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.create_reminder("Call the plumber")
        notice = fw.to_notice(reminder)
        assert notice is not None
        assert notice["type"] == "tier3_recommend"
        for action in notice["suggested_actions"]:
            assert isinstance(action["command"], str)
            assert "capability_id" not in action["command"].lower()
            assert "executor" not in action["command"].lower()
            assert "GovernorMediator" not in action["command"]

    def test_reminder_is_frozen(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.create_reminder("Test")
        with pytest.raises(AttributeError):
            reminder.text = "Modified"


# ---------------------------------------------------------------------------
# Governance isolation — no capability invocations
# ---------------------------------------------------------------------------

class TestReminderNoCapabilityInvocation:

    def test_reminder_framework_does_not_emit_capability_invocation(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.create_reminder("Do the thing")
        notice = fw.to_notice(reminder)
        notice_str = str(notice).lower()
        assert "invoke" not in notice_str or "invocation" not in notice_str
        assert "execute_boundary" not in notice_str
        assert "governor_mediator" not in notice_str

    def test_reminder_framework_does_not_emit_confirmed_true(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.create_reminder("Confirm test")
        notice = fw.to_notice(reminder)
        assert notice.get("confirmed") is None
        assert notice.get("approved") is None
        assert notice.get("auto_execute") is None

    def test_reminder_framework_never_creates_calendar_event(self):
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        reminder = fw.create_reminder("Meeting tomorrow at 3pm")
        notice = fw.to_notice(reminder)
        for action in notice["suggested_actions"]:
            cmd = action["command"].lower()
            assert "create event" not in cmd
            assert "calendar" not in cmd
            assert "cap 57" not in cmd
            assert "cap_57" not in cmd

    def test_reminder_framework_never_persists_memory_directly(self):
        """ReminderFramework has no save/persist/write methods."""
        from src.personality.reminder_framework import ReminderFramework
        fw = ReminderFramework()
        assert not hasattr(fw, "save")
        assert not hasattr(fw, "persist")
        assert not hasattr(fw, "write")
        assert not hasattr(fw, "store")
        assert not hasattr(fw, "commit")


# ---------------------------------------------------------------------------
# Import boundary
# ---------------------------------------------------------------------------

class TestReminderImportBoundary:

    def _source_path(self) -> Path:
        return (
            Path(__file__).resolve().parents[2]
            / "src" / "personality" / "reminder_framework.py"
        )

    def test_reminder_framework_has_no_governance_imports(self):
        source = self._source_path().read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = ""
                if isinstance(node, ast.ImportFrom) and node.module:
                    module = node.module
                elif isinstance(node, ast.Import):
                    module = ".".join(a.name for a in node.names)
                module_lower = module.lower()
                assert "governor" not in module_lower, (
                    f"Governance import: {module}"
                )
                assert "executor" not in module_lower, (
                    f"Executor import: {module}"
                )
                assert "ledger" not in module_lower, (
                    f"Ledger import: {module}"
                )
                assert "network_mediator" not in module_lower, (
                    f"NetworkMediator import: {module}"
                )

    def test_reminder_framework_has_no_store_or_client_imports(self):
        source = self._source_path().read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = ""
                if isinstance(node, ast.ImportFrom) and node.module:
                    module = node.module
                elif isinstance(node, ast.Import):
                    module = ".".join(a.name for a in node.names)
                module_lower = module.lower()
                assert "memory" not in module_lower, (
                    f"Memory store import: {module}"
                )
                assert "connector" not in module_lower, (
                    f"Connector import: {module}"
                )
                assert "shopify" not in module_lower, (
                    f"Shopify import: {module}"
                )
                assert "calendar" not in module_lower, (
                    f"Calendar import: {module}"
                )
