# tests/goals/test_goals_api.py
"""
Goals API endpoint tests.

Uses FastAPI TestClient to verify HTTP behavior of
GET/POST/PUT /api/goals endpoints.
"""
import pytest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.goals_api import build_goals_router
from src.goals.goal_store import GoalStore


@pytest.fixture
def tmp_store(tmp_path):
    """Create a GoalStore backed by a temp file."""
    return GoalStore(path=tmp_path / "goals.json")


@pytest.fixture
def client(tmp_store):
    app = FastAPI()
    router = build_goals_router()
    app.include_router(router)

    # The route handlers do `from src.goals.goal_store import goal_store`
    # so we patch the singleton at the module level.
    with patch(
        "src.goals.goal_store.goal_store", tmp_store
    ):
        yield TestClient(app)


@pytest.fixture
def sample_body():
    return {
        "title": "Test API goal",
        "status": "planning",
        "steps": [
            {
                "step_id": "s1",
                "title": "First step",
                "status": "planned",
            }
        ],
    }


# ── GET /api/goals ──────────────────────────────────


class TestListGoals:
    def test_empty_list(self, client):
        resp = client.get("/api/goals")
        assert resp.status_code == 200
        assert resp.json() == {"goals": []}

    def test_list_after_create(self, client, sample_body):
        client.post("/api/goals", json=sample_body)
        resp = client.get("/api/goals")
        assert resp.status_code == 200
        goals = resp.json()["goals"]
        assert len(goals) == 1
        assert goals[0]["title"] == "Test API goal"


# ── GET /api/goals/{id} ────────────────────────────


class TestGetGoal:
    def test_get_existing(self, client, sample_body):
        create_resp = client.post("/api/goals", json=sample_body)
        goal_id = create_resp.json()["goal_id"]

        resp = client.get(f"/api/goals/{goal_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Test API goal"

    def test_get_not_found(self, client):
        resp = client.get("/api/goals/nonexistent")
        assert resp.status_code == 404


# ── POST /api/goals ─────────────────────────────────


class TestCreateGoal:
    def test_create_returns_201(self, client, sample_body):
        resp = client.post("/api/goals", json=sample_body)
        assert resp.status_code == 201

    def test_create_auto_id(self, client):
        resp = client.post(
            "/api/goals", json={"title": "Auto ID goal"}
        )
        assert resp.status_code == 201
        assert resp.json()["goal_id"].startswith("goal_")

    def test_create_with_explicit_id(self, client):
        resp = client.post(
            "/api/goals",
            json={"goal_id": "my_goal", "title": "Explicit ID"},
        )
        assert resp.status_code == 201
        assert resp.json()["goal_id"] == "my_goal"

    def test_create_rejects_empty_title(self, client):
        resp = client.post("/api/goals", json={"title": ""})
        assert resp.status_code == 400

    def test_create_rejects_invalid_status(self, client):
        resp = client.post(
            "/api/goals",
            json={"title": "Bad", "status": "executing"},
        )
        assert resp.status_code == 400

    def test_create_duplicate_id_rejected(self, client):
        body = {"goal_id": "dup", "title": "First"}
        client.post("/api/goals", json=body)
        resp = client.post("/api/goals", json=body)
        assert resp.status_code == 400


# ── PUT /api/goals/{id} ────────────────────────────


class TestUpdateGoal:
    def test_update_status(self, client, sample_body):
        create_resp = client.post("/api/goals", json=sample_body)
        goal_id = create_resp.json()["goal_id"]

        resp = client.put(
            f"/api/goals/{goal_id}",
            json={"status": "completed"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_update_not_found(self, client):
        resp = client.put(
            "/api/goals/nonexistent",
            json={"status": "planning"},
        )
        assert resp.status_code == 404

    def test_update_empty_body_rejected(self, client, sample_body):
        create_resp = client.post("/api/goals", json=sample_body)
        goal_id = create_resp.json()["goal_id"]

        resp = client.put(f"/api/goals/{goal_id}", json={})
        assert resp.status_code == 400

    def test_update_invalid_status_rejected(
        self, client, sample_body
    ):
        create_resp = client.post("/api/goals", json=sample_body)
        goal_id = create_resp.json()["goal_id"]

        resp = client.put(
            f"/api/goals/{goal_id}",
            json={"status": "auto_running"},
        )
        assert resp.status_code == 400


# ── endpoint existence ──────────────────────────────


class TestEndpointAbsence:
    """Prove that execution endpoints do not exist."""

    def test_no_run_endpoint(self, client, sample_body):
        create_resp = client.post("/api/goals", json=sample_body)
        goal_id = create_resp.json()["goal_id"]
        resp = client.post(f"/api/goals/{goal_id}/run")
        assert resp.status_code in (404, 405, 422)

    def test_no_execute_endpoint(self, client, sample_body):
        create_resp = client.post("/api/goals", json=sample_body)
        goal_id = create_resp.json()["goal_id"]
        resp = client.post(f"/api/goals/{goal_id}/execute")
        assert resp.status_code in (404, 405, 422)

    def test_no_schedule_endpoint(self, client, sample_body):
        create_resp = client.post("/api/goals", json=sample_body)
        goal_id = create_resp.json()["goal_id"]
        resp = client.post(f"/api/goals/{goal_id}/schedule")
        assert resp.status_code in (404, 405, 422)

    def test_no_delete_endpoint(self, client, sample_body):
        create_resp = client.post("/api/goals", json=sample_body)
        goal_id = create_resp.json()["goal_id"]
        resp = client.delete(f"/api/goals/{goal_id}")
        assert resp.status_code in (404, 405)
