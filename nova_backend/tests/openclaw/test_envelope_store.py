"""Unit tests for EnvelopeStore (hardening Step 3)."""
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from src.openclaw.envelope_store import (
    EnvelopeRecord,
    EnvelopeStatus,
    EnvelopeStore,
    EnvelopeStoreError,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _make_store(tmp_path: Path) -> EnvelopeStore:
    return EnvelopeStore(store_path=tmp_path / "envelopes.json")


def _register(store: EnvelopeStore, *, ttl_seconds: int = 300, **kwargs) -> str:
    eid = uuid4()
    now = _utc_now()
    defaults = dict(
        envelope_id=eid,
        envelope_data={"id": str(eid), "title": "Test", "template_id": "test"},
        issuing_channel="manual",
        settings_hash="abc123",
        feature_flags_snapshot={"NOVA_FEATURE_ENVELOPE_FACTORY": True},
        issued_at=now,
        expires_at=now + timedelta(seconds=ttl_seconds),
    )
    defaults.update(kwargs)
    store.register(**defaults)
    return str(eid)


class TestEnvelopeStatus:
    def test_issued_to_running_is_allowed(self):
        assert EnvelopeStatus.transition_allowed("issued", "running")

    def test_issued_to_completed_is_not_allowed(self):
        assert not EnvelopeStatus.transition_allowed("issued", "completed")

    def test_running_to_completed_is_allowed(self):
        assert EnvelopeStatus.transition_allowed("running", "completed")

    def test_running_to_awaiting_approval_is_allowed(self):
        assert EnvelopeStatus.transition_allowed("running", "awaiting_approval")

    def test_completed_is_terminal(self):
        assert EnvelopeStatus.is_terminal("completed")
        assert not EnvelopeStatus.transition_allowed("completed", "running")

    def test_awaiting_approval_never_expires(self):
        record = EnvelopeRecord(
            envelope_id="x",
            status=EnvelopeStatus.AWAITING_APPROVAL,
            created_at=_utc_now().isoformat(),
            updated_at=_utc_now().isoformat(),
            expires_at=(_utc_now() - timedelta(hours=1)).isoformat(),  # past!
            issuing_channel="manual",
            settings_hash="h",
        )
        assert not record.is_expired()


class TestEnvelopeStoreRegister:
    def test_register_creates_record(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store)
        record = store.get(eid)
        assert record is not None
        assert record.status == EnvelopeStatus.ISSUED
        assert record.issuing_channel == "manual"

    def test_registered_record_persists_to_disk(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store)
        store2 = _make_store(tmp_path)
        assert store2.get(eid) is not None

    def test_envelope_data_stored(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store, envelope_data={"id": "x", "title": "My Task"})
        record = store.get(eid)
        assert record.envelope_data["title"] == "My Task"


class TestEnvelopeStoreTransition:
    def test_valid_transition_updates_status(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store)
        store.transition(eid, EnvelopeStatus.RUNNING)
        record = store.get(eid)
        assert record.status == EnvelopeStatus.RUNNING

    def test_invalid_transition_raises(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store)
        with pytest.raises(EnvelopeStoreError, match="Invalid transition"):
            store.transition(eid, EnvelopeStatus.COMPLETED)

    def test_unknown_envelope_raises(self, tmp_path):
        store = _make_store(tmp_path)
        with pytest.raises(EnvelopeStoreError, match="not found"):
            store.transition("nonexistent-id", EnvelopeStatus.RUNNING)

    def test_full_lifecycle(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store)
        store.transition(eid, EnvelopeStatus.RUNNING)
        store.transition(eid, EnvelopeStatus.AWAITING_APPROVAL)
        store.transition(eid, EnvelopeStatus.RUNNING)
        store.transition(eid, EnvelopeStatus.COMPLETED)
        record = store.get(eid)
        assert record.status == EnvelopeStatus.COMPLETED


class TestEnvelopeStoreMarkUsed:
    def test_mark_used_sets_used_at(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store)
        store.mark_used(eid)
        record = store.get(eid)
        assert record.used_at is not None

    def test_double_use_raises(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store)
        store.mark_used(eid)
        with pytest.raises(EnvelopeStoreError, match="already been used"):
            store.mark_used(eid)


class TestEnvelopeStoreTTL:
    def test_expired_envelope_returns_none(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store, ttl_seconds=-1)  # already expired
        record = store.get(eid)
        assert record is None

    def test_expired_envelope_gets_expired_status(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store, ttl_seconds=-1)
        store.get(eid)  # triggers expiry write
        # Read raw file to verify status was updated
        raw = json.loads((tmp_path / "envelopes.json").read_text())
        assert raw[eid]["status"] == EnvelopeStatus.EXPIRED

    def test_transition_on_expired_saves_expiry_to_disk(self, tmp_path):
        """Regression: transition() must persist EXPIRED status before raising."""
        store = _make_store(tmp_path)
        eid = _register(store, ttl_seconds=-1)
        with pytest.raises(EnvelopeStoreError):
            store.transition(eid, EnvelopeStatus.RUNNING)
        raw = json.loads((tmp_path / "envelopes.json").read_text())
        assert raw[eid]["status"] == EnvelopeStatus.EXPIRED
        assert raw[eid]["invalidated_reason"] == "ttl_expired"

    def test_awaiting_approval_does_not_expire(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store, ttl_seconds=300)
        store.transition(eid, EnvelopeStatus.RUNNING)
        store.transition(eid, EnvelopeStatus.AWAITING_APPROVAL)
        # Now force expire by manipulating stored data directly
        raw = json.loads((tmp_path / "envelopes.json").read_text())
        raw[eid]["expires_at"] = (_utc_now() - timedelta(hours=1)).isoformat()
        (tmp_path / "envelopes.json").write_text(json.dumps(raw))
        record = store.get(eid)
        assert record is not None  # still visible because AWAITING_APPROVAL


class TestEnvelopeStoreListActive:
    def test_lists_non_terminal_records(self, tmp_path):
        store = _make_store(tmp_path)
        eid1 = _register(store)
        eid2 = _register(store)
        store.transition(eid2, EnvelopeStatus.RUNNING)
        store.transition(eid2, EnvelopeStatus.COMPLETED)
        active = store.list_active()
        ids = [r.envelope_id for r in active]
        assert eid1 in ids
        assert eid2 not in ids

    def test_expired_records_excluded_from_active(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store, ttl_seconds=-1)
        active = store.list_active()
        assert not any(r.envelope_id == eid for r in active)


class TestEnvelopeStoreRunMetadata:
    def test_update_run_metadata_merges(self, tmp_path):
        store = _make_store(tmp_path)
        eid = _register(store)
        store.update_run_metadata(eid, {"suspended_step": "step-3", "tool": "write_file"})
        store.update_run_metadata(eid, {"suspension_token": "tok-abc"})
        record = store.get(eid)
        assert record.run_metadata["suspended_step"] == "step-3"
        assert record.run_metadata["suspension_token"] == "tok-abc"
