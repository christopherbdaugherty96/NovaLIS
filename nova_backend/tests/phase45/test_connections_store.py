from __future__ import annotations

"""Tests for ConnectionsStore."""

import os
import json
import tempfile
from pathlib import Path

import pytest

from src.connections.connections_store import ConnectionsStore, PROVIDER_REGISTRY, _mask_key


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_store(tmp_path: Path) -> ConnectionsStore:
    return ConnectionsStore(path=tmp_path / "provider_keys.json")


# ---------------------------------------------------------------------------
# Registry sanity
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_all_required_fields_present(self):
        for pid, meta in PROVIDER_REGISTRY.items():
            for field in ("label", "description", "env_var", "kind", "placeholder"):
                assert field in meta, f"Provider {pid!r} missing field {field!r}"

    def test_known_providers_exist(self):
        for pid in ("openai", "brave", "news", "weather", "calendar", "bridge"):
            assert pid in PROVIDER_REGISTRY

    def test_kinds_are_valid(self):
        valid = {"api_key", "file_path", "token"}
        for pid, meta in PROVIDER_REGISTRY.items():
            assert meta["kind"] in valid, f"{pid} has invalid kind {meta['kind']!r}"

    def test_calendar_provider_points_to_calendar_snapshot_capability(self):
        assert PROVIDER_REGISTRY["calendar"]["caps"] == ["57"]


# ---------------------------------------------------------------------------
# Key masking helper
# ---------------------------------------------------------------------------

class TestMaskKey:
    def test_short_key_returns_stars(self):
        assert _mask_key("abc") == "***"

    def test_long_key_shows_hint(self):
        result = _mask_key("sk-abcdefghij")
        assert result.startswith("sk-a")
        assert "..." in result

    def test_empty_key_returns_stars(self):
        assert _mask_key("") == "***"


# ---------------------------------------------------------------------------
# Snapshot / defaults
# ---------------------------------------------------------------------------

class TestSnapshot:
    def test_snapshot_returns_all_providers(self, tmp_path):
        store = _make_store(tmp_path)
        snap = store.snapshot()
        ids = {p["id"] for p in snap}
        for pid in PROVIDER_REGISTRY:
            assert pid in ids

    def test_default_has_key_false(self, tmp_path):
        store = _make_store(tmp_path)
        for p in store.snapshot():
            assert p["has_key"] is False

    def test_default_connected_false(self, tmp_path):
        store = _make_store(tmp_path)
        for p in store.snapshot():
            assert p["connected"] is False

    def test_no_key_values_in_snapshot(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("openai", "sk-secretsecret")
        for p in store.snapshot():
            assert "sk-secretsecret" not in str(p)


# ---------------------------------------------------------------------------
# save_key
# ---------------------------------------------------------------------------

class TestSaveKey:
    def test_save_sets_has_key(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("openai", "sk-testkey12345")
        snap = {p["id"]: p for p in store.snapshot()}
        assert snap["openai"]["has_key"] is True

    def test_save_updates_env_var(self, tmp_path):
        store = _make_store(tmp_path)
        # Clean env first
        os.environ.pop("OPENAI_API_KEY", None)
        store.save_key("openai", "sk-testkey12345")
        assert os.environ.get("OPENAI_API_KEY") == "sk-testkey12345"
        # Cleanup
        os.environ.pop("OPENAI_API_KEY", None)

    def test_save_resets_health(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("openai", "sk-testkey12345")
        store.record_health("openai", ok=True, detail="OK")
        store.save_key("openai", "sk-newkey99999")
        snap = {p["id"]: p for p in store.snapshot()}
        assert snap["openai"]["health_ok"] is None

    def test_unknown_provider_raises(self, tmp_path):
        store = _make_store(tmp_path)
        with pytest.raises(KeyError):
            store.save_key("nonexistent_provider", "key")

    def test_persisted_to_disk(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("brave", "BSA-testkey999")
        raw = json.loads((tmp_path / "provider_keys.json").read_text())
        assert raw["providers"]["brave"]["key"] == "BSA-testkey999"


# ---------------------------------------------------------------------------
# record_health
# ---------------------------------------------------------------------------

class TestRecordHealth:
    def test_health_ok_true(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("openai", "sk-testkey12345")
        store.record_health("openai", ok=True, detail="All good")
        snap = {p["id"]: p for p in store.snapshot()}
        assert snap["openai"]["health_ok"] is True
        assert snap["openai"]["health_detail"] == "All good"

    def test_health_ok_false(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("openai", "sk-badkey")
        store.record_health("openai", ok=False, detail="401 invalid")
        snap = {p["id"]: p for p in store.snapshot()}
        assert snap["openai"]["health_ok"] is False

    def test_connected_true_only_when_key_and_health_ok(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("openai", "sk-testkey12345")
        store.record_health("openai", ok=True)
        snap = {p["id"]: p for p in store.snapshot()}
        assert snap["openai"]["connected"] is True

    def test_connected_false_when_health_fails(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("openai", "sk-testkey12345")
        store.record_health("openai", ok=False)
        snap = {p["id"]: p for p in store.snapshot()}
        assert snap["openai"]["connected"] is False


# ---------------------------------------------------------------------------
# clear_key
# ---------------------------------------------------------------------------

class TestClearKey:
    def test_clear_removes_key(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("brave", "BSA-key123456")
        store.clear_key("brave")
        snap = {p["id"]: p for p in store.snapshot()}
        assert snap["brave"]["has_key"] is False

    def test_clear_removes_env_var(self, tmp_path):
        store = _make_store(tmp_path)
        os.environ["BRAVE_API_KEY"] = "BSA-key123456"
        store.save_key("brave", "BSA-key123456")
        store.clear_key("brave")
        assert os.environ.get("BRAVE_API_KEY") is None

    def test_clear_unknown_provider_raises(self, tmp_path):
        store = _make_store(tmp_path)
        with pytest.raises(KeyError):
            store.clear_key("unknown_provider")


# ---------------------------------------------------------------------------
# clear_all
# ---------------------------------------------------------------------------

class TestClearAll:
    def test_clear_all_removes_every_key(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("openai", "sk-key1234567")
        store.save_key("news", "newskey123456")
        store.clear_all()
        for p in store.snapshot():
            assert p["has_key"] is False

    def test_clear_all_clears_env_vars(self, tmp_path):
        store = _make_store(tmp_path)
        os.environ["OPENAI_API_KEY"] = "sk-key1234567"
        os.environ["NEWS_API_KEY"] = "newskey123456"
        store.save_key("openai", "sk-key1234567")
        store.save_key("news", "newskey123456")
        store.clear_all()
        assert os.environ.get("OPENAI_API_KEY") is None
        assert os.environ.get("NEWS_API_KEY") is None


# ---------------------------------------------------------------------------
# get_key (internal use — returns raw value)
# ---------------------------------------------------------------------------

class TestGetKey:
    def test_returns_raw_key(self, tmp_path):
        store = _make_store(tmp_path)
        store.save_key("weather", "vcweather123456")
        assert store.get_key("weather") == "vcweather123456"

    def test_returns_empty_when_not_set(self, tmp_path):
        store = _make_store(tmp_path)
        assert store.get_key("weather") == ""


# ---------------------------------------------------------------------------
# Persistence — reload from disk
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_second_instance_reads_stored_keys(self, tmp_path):
        path = tmp_path / "provider_keys.json"
        s1 = ConnectionsStore(path=path)
        s1.save_key("news", "newskey123456789")
        s2 = ConnectionsStore(path=path)
        assert s2.get_key("news") == "newskey123456789"
