from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.profiles.user_profile_store import UserProfileStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_store() -> tuple[UserProfileStore, Path]:
    """Return a fresh store backed by a temp directory."""
    tmp = Path(tempfile.mkdtemp())
    path = tmp / "user_profile.json"
    store = UserProfileStore(path=path)
    return store, path


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

class TestDefaults:
    def test_snapshot_returns_expected_keys(self):
        store, _ = _make_store()
        snap = store.snapshot()
        assert "name" in snap
        assert "nickname" in snap
        assert "email" in snap
        assert "rules" in snap
        assert "display_name" in snap
        assert "preferences" in snap
        assert "is_set_up" in snap
        assert "updated_at" in snap

    def test_default_name_is_empty(self):
        store, _ = _make_store()
        assert store.snapshot()["name"] == ""

    def test_default_is_set_up_is_false(self):
        store, _ = _make_store()
        assert store.snapshot()["is_set_up"] is False

    def test_default_response_style_is_balanced(self):
        store, _ = _make_store()
        assert store.snapshot()["preferences"]["response_style"] == "balanced"

    def test_default_use_name_in_responses_is_true(self):
        store, _ = _make_store()
        assert store.snapshot()["preferences"]["use_name_in_responses"] is True

    def test_default_proactive_suggestions_is_true(self):
        store, _ = _make_store()
        assert store.snapshot()["preferences"]["proactive_suggestions"] is True

    def test_default_morning_brief_enabled_is_false(self):
        store, _ = _make_store()
        assert store.snapshot()["preferences"]["morning_brief_enabled"] is False

    def test_schema_version_present(self):
        store, _ = _make_store()
        assert store.snapshot()["schema_version"] == "1.0"


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

class TestSetIdentity:
    def test_set_name(self):
        store, _ = _make_store()
        snap = store.set_identity(name="Chris")
        assert snap["name"] == "Chris"
        assert snap["is_set_up"] is True

    def test_set_nickname(self):
        store, _ = _make_store()
        snap = store.set_identity(name="Chris", nickname="Boss")
        assert snap["nickname"] == "Boss"

    def test_display_name_prefers_nickname(self):
        store, _ = _make_store()
        snap = store.set_identity(name="Chris", nickname="Boss")
        assert snap["display_name"] == "Boss"

    def test_display_name_falls_back_to_name(self):
        store, _ = _make_store()
        snap = store.set_identity(name="Chris")
        assert snap["display_name"] == "Chris"

    def test_set_email(self):
        store, _ = _make_store()
        snap = store.set_identity(email="chris@example.com")
        assert snap["email"] == "chris@example.com"

    def test_name_max_length_enforced(self):
        store, _ = _make_store()
        long_name = "A" * 200
        snap = store.set_identity(name=long_name)
        assert len(snap["name"]) <= 80

    def test_nickname_max_length_enforced(self):
        store, _ = _make_store()
        long = "B" * 200
        snap = store.set_identity(nickname=long)
        assert len(snap["nickname"]) <= 40

    def test_email_max_length_enforced(self):
        store, _ = _make_store()
        long = "c" * 200 + "@x.com"
        snap = store.set_identity(email=long)
        assert len(snap["email"]) <= 120

    def test_partial_update_preserves_existing_fields(self):
        store, _ = _make_store()
        store.set_identity(name="Chris", nickname="Boss")
        snap = store.set_identity(email="chris@example.com")
        assert snap["name"] == "Chris"
        assert snap["nickname"] == "Boss"
        assert snap["email"] == "chris@example.com"

    def test_updated_at_changes_on_save(self):
        store, _ = _make_store()
        t1 = store.snapshot()["updated_at"]
        store.set_identity(name="Chris")
        t2 = store.snapshot()["updated_at"]
        assert t2 >= t1


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------

class TestSetPreferences:
    def test_response_style_concise(self):
        store, _ = _make_store()
        snap = store.set_preferences(response_style="concise")
        assert snap["preferences"]["response_style"] == "concise"

    def test_response_style_detailed(self):
        store, _ = _make_store()
        snap = store.set_preferences(response_style="detailed")
        assert snap["preferences"]["response_style"] == "detailed"

    def test_invalid_response_style_raises(self):
        store, _ = _make_store()
        with pytest.raises(ValueError):
            store.set_preferences(response_style="verbose")

    def test_response_style_case_insensitive(self):
        store, _ = _make_store()
        snap = store.set_preferences(response_style="Concise")
        assert snap["preferences"]["response_style"] == "concise"

    def test_toggle_use_name(self):
        store, _ = _make_store()
        snap = store.set_preferences(use_name_in_responses=False)
        assert snap["preferences"]["use_name_in_responses"] is False

    def test_toggle_proactive_suggestions(self):
        store, _ = _make_store()
        snap = store.set_preferences(proactive_suggestions=False)
        assert snap["preferences"]["proactive_suggestions"] is False

    def test_toggle_morning_brief(self):
        store, _ = _make_store()
        snap = store.set_preferences(morning_brief_enabled=True, morning_brief_time="08:30")
        assert snap["preferences"]["morning_brief_enabled"] is True
        assert snap["preferences"]["morning_brief_time"] == "08:30"

    def test_morning_brief_time_truncated_to_5_chars(self):
        store, _ = _make_store()
        snap = store.set_preferences(morning_brief_time="08:30:00")
        assert snap["preferences"]["morning_brief_time"] == "08:30"


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

class TestSetRules:
    def test_set_rules(self):
        store, _ = _make_store()
        snap = store.set_rules("- Always be concise\n- No filler words")
        assert "Always be concise" in snap["rules"]

    def test_rules_max_length_enforced(self):
        store, _ = _make_store()
        long_rules = "x" * 3000
        snap = store.set_rules(long_rules)
        assert len(snap["rules"]) <= 2000

    def test_empty_rules_clears_field(self):
        store, _ = _make_store()
        store.set_rules("some rules")
        snap = store.set_rules("")
        assert snap["rules"] == ""


# ---------------------------------------------------------------------------
# Persistence (JSON file written correctly)
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_state_persists_to_disk(self):
        store, path = _make_store()
        store.set_identity(name="Chris")
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw["name"] == "Chris"

    def test_new_store_instance_reads_persisted_state(self):
        _, path = _make_store()
        s1 = UserProfileStore(path=path)
        s1.set_identity(name="Chris", nickname="Boss")
        s2 = UserProfileStore(path=path)
        snap = s2.snapshot()
        assert snap["name"] == "Chris"
        assert snap["nickname"] == "Boss"


# ---------------------------------------------------------------------------
# Memory record
# ---------------------------------------------------------------------------

class TestAsMemoryRecord:
    def test_record_has_required_keys(self):
        store, _ = _make_store()
        record = store.as_memory_record()
        for key in ("key", "title", "body", "scope", "source", "protected"):
            assert key in record, f"Missing key: {key}"

    def test_record_source_is_user_profile_setup(self):
        store, _ = _make_store()
        assert store.as_memory_record()["source"] == "user_profile_setup"

    def test_record_scope_is_nova_core(self):
        store, _ = _make_store()
        assert store.as_memory_record()["scope"] == "nova_core"

    def test_record_protected_is_true(self):
        store, _ = _make_store()
        assert store.as_memory_record()["protected"] is True

    def test_record_body_contains_name(self):
        store, _ = _make_store()
        store.set_identity(name="Chris")
        body = store.as_memory_record()["body"]
        assert "Chris" in body

    def test_record_body_contains_email(self):
        store, _ = _make_store()
        store.set_identity(name="Chris", email="chris@example.com")
        body = store.as_memory_record()["body"]
        assert "chris@example.com" in body

    def test_record_body_contains_rules(self):
        store, _ = _make_store()
        store.set_identity(name="Chris")
        store.set_rules("No filler words")
        body = store.as_memory_record()["body"]
        assert "No filler words" in body

    def test_record_title_contains_display_name(self):
        store, _ = _make_store()
        store.set_identity(name="Chris", nickname="Boss")
        title = store.as_memory_record()["title"]
        assert "Boss" in title

    def test_record_title_placeholder_when_no_name(self):
        store, _ = _make_store()
        title = store.as_memory_record()["title"]
        assert "not set" in title
