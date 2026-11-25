from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from src import brain_server
from src.api import audit_api
from src.governor.git_child_admission import GitIdentityOperation


def _identity_results(*, commit: str = "a" * 40, dirty: bool = False):
    return {
        GitIdentityOperation.COMMIT: SimpleNamespace(stdout=commit + "\n", returncode=0),
        GitIdentityOperation.UNSTAGED: SimpleNamespace(
            stdout="", returncode=1 if dirty else 0
        ),
        GitIdentityOperation.STAGED: SimpleNamespace(stdout="", returncode=0),
        GitIdentityOperation.UNTRACKED: SimpleNamespace(stdout="", returncode=0),
    }


def test_phase_status_returns_phase_fields():
    client = TestClient(brain_server.app)

    response = client.get("/phase-status")

    assert response.status_code == 200
    data = response.json()
    assert "phase" in data
    assert "execution_enabled" in data
    assert "delegated_runtime_enabled" in data


def test_phase_status_delegated_runtime_always_false():
    client = TestClient(brain_server.app)

    response = client.get("/phase-status")

    data = response.json()
    assert data["delegated_runtime_enabled"] is False


def test_phase_status_returns_phase_display_string():
    client = TestClient(brain_server.app)

    response = client.get("/phase-status")

    data = response.json()
    assert isinstance(data.get("phase_display"), str)
    assert len(data["phase_display"]) > 0


def test_phase_status_reports_running_build_identity(monkeypatch):
    monkeypatch.setattr(audit_api, "run_git_identity_plan", lambda _root: _identity_results())
    client = TestClient(brain_server.app)

    response = client.get("/phase-status")

    identity = response.json()["build_identity"]
    assert identity["git_available"] is True
    assert len(identity["commit_sha"]) == 40
    assert isinstance(identity["working_tree_dirty"], bool)
    assert Path(identity["source_root"]) == Path(audit_api.__file__).resolve().parents[3]


def test_pending_phase_status_keeps_http_and_websocket_responsive(monkeypatch):
    entered = Event()
    release = Event()
    expired = Event()

    def held_identity(_source_root):
        entered.set()
        if not release.wait(timeout=5):
            expired.set()
        return _identity_results()

    monkeypatch.setattr(audit_api, "run_git_identity_plan", held_identity)
    app = FastAPI()
    app.include_router(audit_api.build_audit_router(brain_server))
    app.add_api_websocket_route("/ws", brain_server.websocket_endpoint)

    @app.get("/probe")
    async def probe():
        return {"responsive": True}

    with TestClient(app) as client, ThreadPoolExecutor(max_workers=1) as pool:
        with client.websocket_connect("/ws") as ws:
            pending = pool.submit(client.get, "/phase-status")
            try:
                assert entered.wait(timeout=5), "Git identity work did not start"
                assert client.get("/probe").json() == {"responsive": True}
                assert not expired.is_set(), "HTTP probe waited for Git identity work"

                turn_id = "phase-status-concurrency-probe"
                ws.send_json({"text": "What do I have next?", "turn_id": turn_id})
                replies = []
                while True:
                    frame = ws.receive_json()
                    if frame.get("turn_id") != turn_id:
                        continue
                    if frame["type"] == "chat_done":
                        break
                    if frame["type"] == "chat":
                        replies.append(frame["message"])
                assert any("What you have next" in reply for reply in replies)
                assert not expired.is_set(), "WebSocket turn waited for Git identity work"
                assert not pending.done(), "Status request should still be pending"
            finally:
                release.set()
            assert pending.result(timeout=5).json()["build_identity"]["commit_sha"] == "a" * 40


def test_runtime_build_identity_degrades_when_git_is_unavailable(monkeypatch):
    def _raise(*_args, **_kwargs):
        raise audit_api.GitChildAdmissionError("git unavailable")

    monkeypatch.setattr(audit_api, "run_git_identity_plan", _raise)

    identity = audit_api._runtime_build_identity()

    assert identity["git_available"] is False
    assert identity["commit_sha"] is None
    assert identity["working_tree_dirty"] is None
    assert identity["source_root"]


def test_runtime_build_identity_uses_content_and_untracked_state(monkeypatch):
    monkeypatch.setattr(
        audit_api,
        "run_git_identity_plan",
        lambda _root: _identity_results(),
    )

    identity = audit_api._runtime_build_identity()

    assert identity["git_available"] is True
    assert identity["commit_sha"] == "a" * 40
    assert identity["working_tree_dirty"] is False


def test_audit_runtime_truth_returns_structured_report():
    client = TestClient(brain_server.app)

    response = client.get("/system/audit/runtime-truth")

    assert response.status_code == 200
    data = response.json()
    # Runtime truth audit must return a dict with at minimum a phase indicator
    assert isinstance(data, dict)


def test_audit_runtime_truth_markdown_returns_text():
    client = TestClient(brain_server.app)

    response = client.get("/system/audit/runtime-truth.md")

    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    assert len(response.text) > 0
