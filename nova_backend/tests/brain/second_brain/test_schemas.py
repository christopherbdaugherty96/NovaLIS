"""Tests for Second Brain schemas.

Invariants under test:
  1. KnowledgeEntry.non_authorizing is always True (enforced)
  2. Valid entries pass validation
  3. Promoted entries require review metadata
  4. Synthesis entries cannot claim runtime_truth_reference
  5. Relationship 'proves' requires source_ref or ledger_ref
  6. KnowledgeEvent validates entity_id/scope_id requirements
  7. Content hash format enforced
  8. ID pattern enforced
"""

from __future__ import annotations

import pytest

from src.brain.second_brain.schemas import (
    AuthorityLabel,
    Confidence,
    EntryStatus,
    EntryType,
    EventActor,
    EventSource,
    EventSubjectType,
    KnowledgeEntry,
    KnowledgeEvent,
    KnowledgeEventType,
    Relationship,
    RelationshipType,
    ReviewState,
    compute_content_hash,
)

_VALID_HASH = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def _valid_entry(**overrides) -> KnowledgeEntry:
    defaults = dict(
        id="kb_test_one",
        schema_version=1,
        title="Test Entry",
        entry_type=EntryType.RESEARCH,
        status=EntryStatus.CANDIDATE,
        authority_label=AuthorityLabel.CANDIDATE_KNOWLEDGE,
        created_at="2026-06-01T00:00:00Z",
        updated_at="2026-06-01T00:00:00Z",
        source_refs=(),
        content_hash=_VALID_HASH,
        review_state=ReviewState.UNREVIEWED,
        confidence=Confidence.MEDIUM,
        project_scope="NovaLIS",
        tags=("test",),
        relationships=(),
    )
    defaults.update(overrides)
    return KnowledgeEntry(**defaults)


def _valid_event(**overrides) -> KnowledgeEvent:
    defaults = dict(
        event_id="kbevt_test_1",
        seq=1,
        schema_version=1,
        occurred_at="2026-06-01T00:00:00Z",
        event_type=KnowledgeEventType.CAPTURED,
        subject_type=EventSubjectType.ENTRY,
        idempotency_key="idem-1",
        source=EventSource.MANUAL,
        actor=EventActor.USER,
        authority_label=AuthorityLabel.RAW_SOURCE,
        payload_hash=_VALID_HASH,
        entity_id="kb_test_one",
        entity_version=1,
    )
    defaults.update(overrides)
    return KnowledgeEvent(**defaults)


# -------------------------------------------------------------------
# KnowledgeEntry — non_authorizing invariant
# -------------------------------------------------------------------

class TestNonAuthorizingInvariant:
    def test_non_authorizing_always_true(self):
        entry = _valid_entry()
        assert entry.non_authorizing is True

    def test_non_authorizing_cannot_be_overridden_false(self):
        entry = _valid_entry(non_authorizing=False)
        assert entry.non_authorizing is True

    def test_non_authorizing_in_to_dict(self):
        d = _valid_entry().to_dict()
        assert d["non_authorizing"] is True


# -------------------------------------------------------------------
# KnowledgeEntry — valid entries
# -------------------------------------------------------------------

class TestValidEntry:
    def test_valid_candidate_passes(self):
        assert _valid_entry().validate() == []

    def test_valid_promoted_passes(self):
        entry = _valid_entry(
            status=EntryStatus.PROMOTED,
            authority_label=AuthorityLabel.PROMOTED_KNOWLEDGE,
            review_state=ReviewState.APPROVED,
            reviewed_by="reviewer",
            reviewed_at="2026-06-01T00:00:00Z",
            source_refs=("docs/proof.md",),
        )
        assert entry.validate() == []


# -------------------------------------------------------------------
# KnowledgeEntry — promoted without review metadata
# -------------------------------------------------------------------

class TestPromotedValidation:
    def test_promoted_without_review_state_fails(self):
        entry = _valid_entry(
            status=EntryStatus.PROMOTED,
            review_state=ReviewState.UNREVIEWED,
            reviewed_by="reviewer",
            reviewed_at="2026-06-01T00:00:00Z",
            source_refs=("docs/proof.md",),
        )
        errors = entry.validate()
        assert any("review_state" in e.field for e in errors)

    def test_promoted_without_reviewed_by_fails(self):
        entry = _valid_entry(
            status=EntryStatus.PROMOTED,
            review_state=ReviewState.APPROVED,
            reviewed_by="",
            reviewed_at="2026-06-01T00:00:00Z",
            source_refs=("docs/proof.md",),
        )
        errors = entry.validate()
        assert any("reviewed_by" in e.field for e in errors)

    def test_promoted_without_reviewed_at_fails(self):
        entry = _valid_entry(
            status=EntryStatus.PROMOTED,
            review_state=ReviewState.APPROVED,
            reviewed_by="reviewer",
            reviewed_at="",
            source_refs=("docs/proof.md",),
        )
        errors = entry.validate()
        assert any("reviewed_at" in e.field for e in errors)

    def test_promoted_without_source_or_ledger_refs_fails(self):
        entry = _valid_entry(
            status=EntryStatus.PROMOTED,
            review_state=ReviewState.APPROVED,
            reviewed_by="reviewer",
            reviewed_at="2026-06-01T00:00:00Z",
            source_refs=(),
            ledger_refs=(),
        )
        errors = entry.validate()
        assert any("source_refs" in e.field for e in errors)

    def test_promoted_with_ledger_refs_only_passes(self):
        entry = _valid_entry(
            status=EntryStatus.PROMOTED,
            review_state=ReviewState.APPROVED,
            reviewed_by="reviewer",
            reviewed_at="2026-06-01T00:00:00Z",
            source_refs=(),
            ledger_refs=("ledger:abc123",),
        )
        assert entry.validate() == []


# -------------------------------------------------------------------
# KnowledgeEntry — synthesis cannot claim runtime_truth_reference
# -------------------------------------------------------------------

class TestSynthesisAuthority:
    def test_synthesis_runtime_truth_fails(self):
        entry = _valid_entry(
            entry_type=EntryType.SYNTHESIS,
            authority_label=AuthorityLabel.RUNTIME_TRUTH_REFERENCE,
        )
        errors = entry.validate()
        assert any("authority_label" in e.field for e in errors)

    def test_synthesis_candidate_knowledge_passes(self):
        entry = _valid_entry(
            entry_type=EntryType.SYNTHESIS,
            authority_label=AuthorityLabel.CANDIDATE_KNOWLEDGE,
        )
        errors = [
            e for e in entry.validate()
            if "authority_label" in e.field
        ]
        assert errors == []


# -------------------------------------------------------------------
# KnowledgeEntry — format validation
# -------------------------------------------------------------------

class TestFormatValidation:
    def test_bad_id_fails(self):
        entry = _valid_entry(id="not-a-valid-id")
        errors = entry.validate()
        assert any("id" in e.field for e in errors)

    def test_bad_content_hash_fails(self):
        entry = _valid_entry(content_hash="md5:abc")
        errors = entry.validate()
        assert any("content_hash" in e.field for e in errors)

    def test_bad_tag_fails(self):
        entry = _valid_entry(tags=("valid", "has spaces",))
        errors = entry.validate()
        assert any("tags" in e.field for e in errors)

    def test_empty_title_fails(self):
        entry = _valid_entry(title="")
        errors = entry.validate()
        assert any("title" in e.field for e in errors)

    def test_wrong_schema_version_fails(self):
        entry = _valid_entry(schema_version=2)
        errors = entry.validate()
        assert any("schema_version" in e.field for e in errors)


# -------------------------------------------------------------------
# Relationship
# -------------------------------------------------------------------

class TestRelationship:
    def test_valid_supports_passes(self):
        rel = Relationship(
            type=RelationshipType.SUPPORTS,
            target="kb_other",
            confidence=Confidence.HIGH,
        )
        assert rel.validate() == []

    def test_proves_without_evidence_fails(self):
        rel = Relationship(
            type=RelationshipType.PROVES,
            target="kb_other",
            confidence=Confidence.HIGH,
        )
        errors = rel.validate()
        assert any("source_ref" in e.field for e in errors)

    def test_proves_with_source_ref_passes(self):
        rel = Relationship(
            type=RelationshipType.PROVES,
            target="kb_other",
            confidence=Confidence.HIGH,
            source_ref="docs/proof.md",
        )
        assert rel.validate() == []

    def test_proves_with_ledger_ref_passes(self):
        rel = Relationship(
            type=RelationshipType.PROVES,
            target="kb_other",
            confidence=Confidence.HIGH,
            ledger_ref="ledger:abc",
        )
        assert rel.validate() == []

    def test_bad_target_id_fails(self):
        rel = Relationship(
            type=RelationshipType.SUPPORTS,
            target="not_valid",
            confidence=Confidence.HIGH,
        )
        errors = rel.validate()
        assert any("target" in e.field for e in errors)


# -------------------------------------------------------------------
# KnowledgeEvent
# -------------------------------------------------------------------

class TestKnowledgeEvent:
    def test_valid_entry_event_passes(self):
        assert _valid_event().validate() == []

    def test_entry_event_without_entity_id_fails(self):
        event = _valid_event(entity_id="")
        errors = event.validate()
        assert any("entity_id" in e.field for e in errors)

    def test_entry_event_without_entity_version_fails(self):
        event = _valid_event(entity_version=0)
        errors = event.validate()
        assert any("entity_version" in e.field for e in errors)

    def test_index_event_without_scope_id_fails(self):
        event = _valid_event(
            subject_type=EventSubjectType.INDEX,
            entity_id="",
            entity_version=0,
            scope_id="",
        )
        errors = event.validate()
        assert any("scope_id" in e.field for e in errors)

    def test_index_event_with_scope_id_passes(self):
        event = _valid_event(
            subject_type=EventSubjectType.INDEX,
            entity_id="",
            entity_version=0,
            scope_id="vault_main",
        )
        scope_errors = [
            e for e in event.validate()
            if "scope_id" in e.field
        ]
        assert scope_errors == []

    def test_bad_event_id_fails(self):
        event = _valid_event(event_id="bad_id")
        errors = event.validate()
        assert any("event_id" in e.field for e in errors)

    def test_bad_payload_hash_fails(self):
        event = _valid_event(payload_hash="nope")
        errors = event.validate()
        assert any("payload_hash" in e.field for e in errors)

    def test_seq_zero_fails(self):
        event = _valid_event(seq=0)
        errors = event.validate()
        assert any("seq" in e.field for e in errors)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

class TestHelpers:
    def test_compute_content_hash_format(self):
        h = compute_content_hash("hello world")
        assert h.startswith("sha256:")
        assert len(h) == 71

    def test_compute_content_hash_deterministic(self):
        assert compute_content_hash("x") == compute_content_hash("x")

    def test_compute_content_hash_differs(self):
        assert compute_content_hash("a") != compute_content_hash("b")
