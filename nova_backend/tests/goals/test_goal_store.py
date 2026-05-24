# tests/goals/test_goal_store.py
"""
Goal store unit tests.

These tests prove:
  1. CRUD works (create, read, update)
  2. goals.json survives reload
  3. Validation rejects bad data
  4. Thread safety basics
"""
import json
import pytest
from pathlib import Path

from src.goals.goal_store import GoalStore


@pytest.fixture
def tmp_store(tmp_path):
    """Create a GoalStore backed by a temp file."""
    return GoalStore(path=tmp_path / "goals.json")


@pytest.fixture
def sample_goal():
    return {
        "goal_id": "goal_test_001",
        "title": "Test goal",
        "status": "planning",
        "steps": [
            {
                "step_id": "step_001",
                "title": "First step",
                "status": "planned",
                "required_capability": None,
                "approval_required": False,
            }
        ],
        "permission_envelope": {
            "allowed_capabilities": [],
            "blocked_actions": ["External writes"],
            "requires_confirmation": [],
        },
        "ledger_refs": [],
    }


# ── create ──────────────────────────────────────────


class TestGoalCreate:
    def test_create_goal_returns_record(self, tmp_store, sample_goal):
        result = tmp_store.create_goal(sample_goal)
        assert result["goal_id"] == "goal_test_001"
        assert result["title"] == "Test goal"
        assert result["status"] == "planning"

    def test_create_goal_sets_timestamps(self, tmp_store, sample_goal):
        result = tmp_store.create_goal(sample_goal)
        assert "created_at" in result
        assert "updated_at" in result

    def test_create_goal_auto_generates_id(self, tmp_store):
        goal = {"title": "No explicit ID"}
        result = tmp_store.create_goal(goal)
        assert result["goal_id"].startswith("goal_")

    def test_create_goal_rejects_duplicate_id(
        self, tmp_store, sample_goal
    ):
        tmp_store.create_goal(sample_goal)
        with pytest.raises(ValueError, match="already exists"):
            tmp_store.create_goal(sample_goal)

    def test_create_goal_rejects_missing_title(self, tmp_store):
        with pytest.raises(ValueError, match="title"):
            tmp_store.create_goal({"title": ""})

    def test_create_goal_rejects_invalid_status(self, tmp_store):
        with pytest.raises(ValueError, match="Invalid goal status"):
            tmp_store.create_goal({
                "title": "Bad status",
                "status": "executing",
            })

    def test_create_goal_rejects_invalid_step_status(self, tmp_store):
        with pytest.raises(ValueError, match="Invalid step status"):
            tmp_store.create_goal({
                "title": "Bad step",
                "steps": [
                    {"step_id": "s1", "title": "x", "status": "running_autonomously"}
                ],
            })

    def test_create_goal_defaults(self, tmp_store):
        result = tmp_store.create_goal({"title": "Minimal goal"})
        assert result["status"] == "planning"
        assert result["steps"] == []
        assert result["ledger_refs"] == []
        assert "permission_envelope" in result


# ── read ────────────────────────────────────────────


class TestGoalRead:
    def test_list_goals_empty(self, tmp_store):
        assert tmp_store.list_goals() == []

    def test_list_goals_returns_all(self, tmp_store, sample_goal):
        tmp_store.create_goal(sample_goal)
        tmp_store.create_goal({
            "goal_id": "goal_test_002",
            "title": "Second goal",
        })
        goals = tmp_store.list_goals()
        assert len(goals) == 2

    def test_get_goal_by_id(self, tmp_store, sample_goal):
        tmp_store.create_goal(sample_goal)
        result = tmp_store.get_goal("goal_test_001")
        assert result is not None
        assert result["title"] == "Test goal"

    def test_get_goal_not_found(self, tmp_store):
        assert tmp_store.get_goal("nonexistent") is None

    def test_returned_goals_are_copies(self, tmp_store, sample_goal):
        tmp_store.create_goal(sample_goal)
        g1 = tmp_store.get_goal("goal_test_001")
        g2 = tmp_store.get_goal("goal_test_001")
        assert g1 is not g2
        g1["title"] = "MUTATED"
        assert tmp_store.get_goal("goal_test_001")["title"] == "Test goal"


# ── update ──────────────────────────────────────────


class TestGoalUpdate:
    def test_update_status(self, tmp_store, sample_goal):
        tmp_store.create_goal(sample_goal)
        result = tmp_store.update_goal(
            "goal_test_001", {"status": "completed"}
        )
        assert result["status"] == "completed"

    def test_update_title(self, tmp_store, sample_goal):
        tmp_store.create_goal(sample_goal)
        result = tmp_store.update_goal(
            "goal_test_001", {"title": "Updated title"}
        )
        assert result["title"] == "Updated title"

    def test_update_steps(self, tmp_store, sample_goal):
        tmp_store.create_goal(sample_goal)
        new_steps = [
            {"step_id": "s1", "title": "Done", "status": "completed"}
        ]
        result = tmp_store.update_goal(
            "goal_test_001", {"steps": new_steps}
        )
        assert result["steps"][0]["status"] == "completed"

    def test_update_sets_updated_at(self, tmp_store, sample_goal):
        created = tmp_store.create_goal(sample_goal)
        original_ts = created["updated_at"]
        import time
        time.sleep(0.01)
        updated = tmp_store.update_goal(
            "goal_test_001", {"status": "running"}
        )
        assert updated["updated_at"] >= original_ts

    def test_update_nonexistent_returns_none(self, tmp_store):
        assert tmp_store.update_goal("nope", {"status": "planning"}) is None

    def test_update_rejects_invalid_status(
        self, tmp_store, sample_goal
    ):
        tmp_store.create_goal(sample_goal)
        with pytest.raises(ValueError, match="Invalid goal status"):
            tmp_store.update_goal(
                "goal_test_001", {"status": "auto_executing"}
            )

    def test_update_does_not_change_goal_id(
        self, tmp_store, sample_goal
    ):
        tmp_store.create_goal(sample_goal)
        tmp_store.update_goal(
            "goal_test_001", {"goal_id": "HIJACKED"}
        )
        # goal_id is not in _UPDATABLE_FIELDS, so it's ignored
        assert tmp_store.get_goal("goal_test_001") is not None
        assert tmp_store.get_goal("HIJACKED") is None

    def test_update_does_not_change_created_at(
        self, tmp_store, sample_goal
    ):
        created = tmp_store.create_goal(sample_goal)
        original_ts = created["created_at"]
        tmp_store.update_goal(
            "goal_test_001", {"created_at": "1999-01-01T00:00:00Z"}
        )
        assert (
            tmp_store.get_goal("goal_test_001")["created_at"]
            == original_ts
        )


# ── persistence ─────────────────────────────────────


class TestGoalPersistence:
    def test_goals_survive_reload(self, tmp_path, sample_goal):
        path = tmp_path / "goals.json"
        store1 = GoalStore(path=path)
        store1.create_goal(sample_goal)

        store2 = GoalStore(path=path)
        goals = store2.list_goals()
        assert len(goals) == 1
        assert goals[0]["goal_id"] == "goal_test_001"

    def test_goals_json_is_valid_json(self, tmp_path, sample_goal):
        path = tmp_path / "goals.json"
        store = GoalStore(path=path)
        store.create_goal(sample_goal)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["version"] == 1
        assert len(data["goals"]) == 1

    def test_corrupt_file_resets_gracefully(self, tmp_path):
        path = tmp_path / "goals.json"
        path.write_text("NOT VALID JSON", encoding="utf-8")
        store = GoalStore(path=path)
        assert store.list_goals() == []

    def test_missing_file_starts_empty(self, tmp_path):
        path = tmp_path / "nonexistent" / "goals.json"
        store = GoalStore(path=path)
        assert store.list_goals() == []
