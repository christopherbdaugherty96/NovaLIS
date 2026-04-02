from __future__ import annotations

from fastapi.testclient import TestClient

from src import brain_server


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
