from __future__ import annotations

from src.working_context.project_threads import ProjectThreadStore


class _FakeLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, metadata: dict) -> None:
        self.events.append((event_type, metadata))


def test_project_thread_store_create_attach_and_resume_brief():
    ledger = _FakeLedger()
    store = ProjectThreadStore(session_id="sess-1", ledger=ledger)

    created = store.ensure_thread("Deployment Issue", goal="Fix failing deployment pipeline.")
    assert created.name == "Deployment Issue"
    assert store.active_thread_name() == "Deployment Issue"

    store.attach_update(
        thread_name="Deployment Issue",
        summary="ModuleNotFoundError during build step.",
        category="blocker",
        next_steps=["Verify virtual environment", "Check PYTHONPATH in container"],
    )

    found, brief = store.render_brief("Deployment Issue")
    assert found is True
    assert "Continuity Brief" in brief
    assert "ModuleNotFoundError" in brief
    assert "PYTHONPATH" in brief

    event_types = [name for name, _ in ledger.events]
    assert "PROJECT_THREAD_CREATED" in event_types
    assert "PROJECT_THREAD_UPDATED" in event_types
    assert "PROJECT_THREAD_RESUMED" in event_types


def test_project_thread_store_map_widget_includes_active_thread():
    store = ProjectThreadStore(session_id="sess-2", ledger=None)
    store.ensure_thread("AI Governance Research", goal="Track policy updates.")
    store.attach_update(
        thread_name="AI Governance Research",
        summary="Saved EU AI Act screen summary.",
    )

    widget = store.render_map_widget()
    assert widget["type"] == "thread_map"
    assert widget["active_thread"] == "AI Governance Research"
    assert isinstance(widget["threads"], list)
    assert widget["threads"]
    assert widget["threads"][0]["name"] == "AI Governance Research"
    assert widget["threads"][0]["health_state"] in {"blocked", "at-risk", "on-track"}


def test_project_thread_store_status_and_blocker_intelligence():
    store = ProjectThreadStore(session_id="sess-3", ledger=None)
    store.ensure_thread("Release Stabilization", goal="Ship stable release.")
    store.attach_update(thread_name="Release Stabilization", summary="Fixed crash in startup path.")
    store.attach_update(
        thread_name="Release Stabilization",
        summary="Deployment container missing dependency.",
        category="blocker",
        next_steps=["Verify dependency install step", "Rebuild container image"],
    )

    found_status, status_text = store.render_status("release stabilization")
    assert found_status is True
    assert "Project Status" in status_text
    assert "Thread Health" in status_text
    assert "Remaining" in status_text

    found_blocker, blocker_text = store.render_biggest_blocker("release stabilization")
    assert found_blocker is True
    assert "Biggest Blocker" in blocker_text
    assert "missing dependency" in blocker_text.lower()


def test_project_thread_store_resolves_partial_names():
    store = ProjectThreadStore(session_id="sess-4", ledger=None)
    store.ensure_thread("AI Governance Research")
    found, brief = store.render_brief("governance")
    assert found is True
    assert "AI Governance Research" in brief

    found_id, resolved_name, resolved_key = store.resolve_thread_identity("governance")
    assert found_id is True
    assert resolved_name == "AI Governance Research"
    assert resolved_key == "ai governance research"


def test_project_thread_store_most_blocked_project_summary():
    store = ProjectThreadStore(session_id="sess-5", ledger=None)
    store.ensure_thread("Deployment Issue")
    store.attach_update(thread_name="Deployment Issue", summary="Import path failure in container.", category="blocker")
    store.ensure_thread("Docs Cleanup")
    store.attach_update(thread_name="Docs Cleanup", summary="Updated README structure.")
    found, message = store.render_most_blocked()
    assert found is True
    assert "Most Blocked Project" in message
    assert "Deployment Issue" in message


def test_project_thread_store_detail_snapshot():
    store = ProjectThreadStore(session_id="sess-6", ledger=None)
    store.ensure_thread("Deployment Issue", goal="Ship stable deployment.")
    store.attach_update(thread_name="Deployment Issue", summary="Captured stack trace in CI.")
    store.attach_update(
        thread_name="Deployment Issue",
        summary="Container cannot resolve module path.",
        category="blocker",
        next_steps=["Verify PYTHONPATH in container"],
    )
    store.add_decision(thread_name="Deployment Issue", decision="Inspect PYTHONPATH before rebuild.")

    found, detail = store.get_thread_detail("deployment issue")
    assert found is True
    assert detail["name"] == "Deployment Issue"
    assert detail["goal"] == "Ship stable deployment."
    assert "Container cannot resolve module path." in detail["latest_blocker"]
    assert "Inspect PYTHONPATH before rebuild." in detail["latest_decision"]
    assert detail["recent_next_actions"]
