"""Second Brain knowledge schemas.

Python dataclass equivalents of the JSON schemas in
future/brain/second_brain/*.schema.json.

Non-authorizing: every KnowledgeEntry enforces non_authorizing=True.
These objects cannot grant approval, enable capabilities, or substitute
for ledger receipts.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


_KB_ID_RE = re.compile(r"^kb_[A-Za-z0-9][A-Za-z0-9_-]*$")
_CONTENT_HASH_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
_TAG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_/-]*$")
_EVENT_ID_RE = re.compile(r"^kbevt_[A-Za-z0-9][A-Za-z0-9_-]*$")


class EntryType(str, Enum):
    RESEARCH = "research"
    DECISION = "decision"
    PATTERN = "pattern"
    CONVERSATION = "conversation"
    REFERENCE = "reference"
    CAPABILITY_LOG = "capability_log"
    ENTITY = "entity"
    CONCEPT = "concept"
    SYNTHESIS = "synthesis"
    PROPOSAL = "proposal"


class EntryStatus(str, Enum):
    CAPTURED = "captured"
    CANDIDATE = "candidate"
    REVIEWED = "reviewed"
    PROMOTED = "promoted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class AuthorityLabel(str, Enum):
    RAW_SOURCE = "raw_source"
    CANDIDATE_KNOWLEDGE = "candidate_knowledge"
    REVIEWED_KNOWLEDGE = "reviewed_knowledge"
    PROMOTED_KNOWLEDGE = "promoted_knowledge"
    RUNTIME_TRUTH_REFERENCE = "runtime_truth_reference"
    LEDGER_RECEIPT_REFERENCE = "ledger_receipt_reference"


class ReviewState(str, Enum):
    UNREVIEWED = "unreviewed"
    NEEDS_CHANGES = "needs_changes"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class RelationshipType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"
    DERIVED_FROM = "derived_from"
    IMPLEMENTS = "implements"
    BLOCKS = "blocks"
    DEPENDS_ON = "depends_on"
    PROVES = "proves"
    CITES = "cites"
    RELATES_TO = "relates_to"


class KnowledgeEventType(str, Enum):
    CAPTURED = "knowledge.captured"
    PROPOSED = "knowledge.proposed"
    REVIEWED = "knowledge.reviewed"
    PROMOTED = "knowledge.promoted"
    REJECTED = "knowledge.rejected"
    SUPERSEDED = "knowledge.superseded"
    TOMBSTONED = "knowledge.tombstoned"
    ARCHIVED = "knowledge.archived"
    INDEX_REBUILT = "knowledge.index_rebuilt"
    SEARCH_PERFORMED = "knowledge.search_performed"
    GRAPH_SNAPSHOT_CREATED = "knowledge.graph_snapshot_created"


class EventSubjectType(str, Enum):
    ENTRY = "entry"
    RELATIONSHIP = "relationship"
    INDEX = "index"
    SEARCH = "search"
    GRAPH_SNAPSHOT = "graph_snapshot"
    VAULT = "vault"


class EventSource(str, Enum):
    MANUAL = "manual"
    VAULT_SYNC = "vault_sync"
    INDEXER = "indexer"
    PROPOSAL_REVIEW = "proposal_review"
    SEARCH = "search"
    DASHBOARD = "dashboard"


class EventActor(str, Enum):
    USER = "user"
    NOVA = "nova"
    SYSTEM = "system"


# -------------------------------------------------------------------
# Validation errors
# -------------------------------------------------------------------

@dataclass(frozen=True)
class SchemaError:
    field: str
    message: str


# -------------------------------------------------------------------
# Relationship
# -------------------------------------------------------------------

@dataclass(frozen=True)
class Relationship:
    type: RelationshipType
    target: str
    confidence: Confidence
    source_ref: str = ""
    ledger_ref: str = ""
    note: str = ""

    def validate(self) -> list[SchemaError]:
        errors: list[SchemaError] = []
        if not _KB_ID_RE.match(self.target):
            errors.append(SchemaError(
                "target",
                f"Must match kb_* pattern, got {self.target!r}.",
            ))
        if self.type == RelationshipType.PROVES:
            if not self.source_ref and not self.ledger_ref:
                errors.append(SchemaError(
                    "source_ref|ledger_ref",
                    "'proves' relationship requires source_ref or ledger_ref.",
                ))
        return errors

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.type.value,
            "target": self.target,
            "confidence": self.confidence.value,
        }
        if self.source_ref:
            d["source_ref"] = self.source_ref
        if self.ledger_ref:
            d["ledger_ref"] = self.ledger_ref
        if self.note:
            d["note"] = self.note
        return d


# -------------------------------------------------------------------
# KnowledgeEntry
# -------------------------------------------------------------------

@dataclass(frozen=True)
class KnowledgeEntry:
    id: str
    schema_version: int
    title: str
    entry_type: EntryType
    status: EntryStatus
    authority_label: AuthorityLabel
    created_at: str
    updated_at: str
    source_refs: tuple[str, ...]
    content_hash: str
    review_state: ReviewState
    confidence: Confidence
    project_scope: str
    tags: tuple[str, ...]
    relationships: tuple[Relationship, ...]
    supersedes: tuple[str, ...] = ()
    superseded_by: tuple[str, ...] = ()
    ledger_refs: tuple[str, ...] = ()
    reviewed_by: str = ""
    reviewed_at: str = ""
    non_authorizing: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "non_authorizing", True)

    def validate(self) -> list[SchemaError]:
        errors: list[SchemaError] = []

        if not _KB_ID_RE.match(self.id):
            errors.append(SchemaError(
                "id", f"Must match kb_* pattern, got {self.id!r}.",
            ))
        if self.schema_version != 1:
            errors.append(SchemaError(
                "schema_version", f"Must be 1, got {self.schema_version}.",
            ))
        if not self.title.strip():
            errors.append(SchemaError("title", "Must not be empty."))
        if not _CONTENT_HASH_RE.match(self.content_hash):
            errors.append(SchemaError(
                "content_hash",
                f"Must match sha256:<64hex>, got {self.content_hash!r}.",
            ))
        for tag in self.tags:
            if not _TAG_RE.match(tag):
                errors.append(SchemaError("tags", f"Invalid tag {tag!r}."))
        for sid in self.supersedes:
            if not _KB_ID_RE.match(sid):
                errors.append(SchemaError(
                    "supersedes", f"Invalid ID {sid!r}.",
                ))
        for sid in self.superseded_by:
            if not _KB_ID_RE.match(sid):
                errors.append(SchemaError(
                    "superseded_by", f"Invalid ID {sid!r}.",
                ))

        if self.entry_type == EntryType.SYNTHESIS:
            if self.authority_label == AuthorityLabel.RUNTIME_TRUTH_REFERENCE:
                errors.append(SchemaError(
                    "authority_label",
                    "Synthesis entries cannot claim runtime_truth_reference.",
                ))

        if self.status == EntryStatus.PROMOTED:
            if self.review_state != ReviewState.APPROVED:
                errors.append(SchemaError(
                    "review_state",
                    "Promoted entries must have review_state=approved.",
                ))
            if not self.reviewed_by:
                errors.append(SchemaError(
                    "reviewed_by",
                    "Promoted entries require reviewed_by.",
                ))
            if not self.reviewed_at:
                errors.append(SchemaError(
                    "reviewed_at",
                    "Promoted entries require reviewed_at.",
                ))
            if not self.source_refs and not self.ledger_refs:
                errors.append(SchemaError(
                    "source_refs|ledger_refs",
                    "Promoted entries require source_refs or ledger_refs.",
                ))

        for rel in self.relationships:
            errors.extend(rel.validate())

        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "schema_version": self.schema_version,
            "title": self.title,
            "entry_type": self.entry_type.value,
            "status": self.status.value,
            "authority_label": self.authority_label.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source_refs": list(self.source_refs),
            "content_hash": self.content_hash,
            "review_state": self.review_state.value,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
            "confidence": self.confidence.value,
            "project_scope": self.project_scope,
            "tags": list(self.tags),
            "relationships": [r.to_dict() for r in self.relationships],
            "supersedes": list(self.supersedes),
            "superseded_by": list(self.superseded_by),
            "ledger_refs": list(self.ledger_refs),
            "non_authorizing": True,
        }


# -------------------------------------------------------------------
# KnowledgeEvent
# -------------------------------------------------------------------

@dataclass(frozen=True)
class KnowledgeEvent:
    event_id: str
    seq: int
    schema_version: int
    occurred_at: str
    event_type: KnowledgeEventType
    subject_type: EventSubjectType
    idempotency_key: str
    source: EventSource
    actor: EventActor
    authority_label: AuthorityLabel
    payload_hash: str
    entity_id: str = ""
    entity_version: int = 0
    entity_ids: tuple[str, ...] = ()
    scope_id: str = ""
    receipt_ref: str = ""

    def validate(self) -> list[SchemaError]:
        errors: list[SchemaError] = []

        if not _EVENT_ID_RE.match(self.event_id):
            errors.append(SchemaError(
                "event_id",
                f"Must match kbevt_* pattern, got {self.event_id!r}.",
            ))
        if self.seq < 1:
            errors.append(SchemaError("seq", "Must be >= 1."))
        if self.schema_version != 1:
            errors.append(SchemaError(
                "schema_version", f"Must be 1, got {self.schema_version}.",
            ))
        if not self.idempotency_key.strip():
            errors.append(SchemaError(
                "idempotency_key", "Must not be empty.",
            ))
        if not _CONTENT_HASH_RE.match(self.payload_hash):
            errors.append(SchemaError(
                "payload_hash",
                f"Must match sha256:<64hex>, got {self.payload_hash!r}.",
            ))

        if self.subject_type in (
            EventSubjectType.ENTRY,
            EventSubjectType.RELATIONSHIP,
        ):
            if not self.entity_id:
                errors.append(SchemaError(
                    "entity_id",
                    f"Required when subject_type={self.subject_type.value}.",
                ))
            if self.entity_version < 1:
                errors.append(SchemaError(
                    "entity_version",
                    f"Required >= 1 when subject_type={self.subject_type.value}.",
                ))

        if self.subject_type in (
            EventSubjectType.INDEX,
            EventSubjectType.SEARCH,
            EventSubjectType.GRAPH_SNAPSHOT,
            EventSubjectType.VAULT,
        ):
            if not self.scope_id:
                errors.append(SchemaError(
                    "scope_id",
                    f"Required when subject_type={self.subject_type.value}.",
                ))

        return errors

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "event_id": self.event_id,
            "seq": self.seq,
            "schema_version": self.schema_version,
            "occurred_at": self.occurred_at,
            "event_type": self.event_type.value,
            "subject_type": self.subject_type.value,
            "idempotency_key": self.idempotency_key,
            "source": self.source.value,
            "actor": self.actor.value,
            "authority_label": self.authority_label.value,
            "payload_hash": self.payload_hash,
        }
        if self.entity_id:
            d["entity_id"] = self.entity_id
        if self.entity_version:
            d["entity_version"] = self.entity_version
        if self.entity_ids:
            d["entity_ids"] = list(self.entity_ids)
        if self.scope_id:
            d["scope_id"] = self.scope_id
        if self.receipt_ref:
            d["receipt_ref"] = self.receipt_ref
        return d


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def compute_content_hash(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"
