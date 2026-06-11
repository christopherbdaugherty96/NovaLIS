"""Frontmatter parser and wikilink extractor for Obsidian vault notes.

Read-only. Never modifies files. Parses YAML frontmatter and extracts
wikilinks from the Markdown body. Returns structured results that can
feed into vault lint and schema validation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.brain.second_brain.schemas import (
    AuthorityLabel,
    Confidence,
    EntryStatus,
    EntryType,
    KnowledgeEntry,
    Relationship,
    RelationshipType,
    ReviewState,
    SchemaError,
)


_FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?\n)---\s*\n?",
    re.DOTALL,
)

_WIKILINK_RE = re.compile(
    r"\[\[([^\]\|]+?)(?:\|[^\]]+?)?\]\]",
)


# -------------------------------------------------------------------
# Parse results
# -------------------------------------------------------------------

@dataclass(frozen=True)
class ParsedNote:
    path: Path
    frontmatter: dict[str, Any]
    body: str
    wikilinks: tuple[str, ...]
    raw_text: str
    parse_errors: tuple[str, ...]

    @property
    def has_frontmatter(self) -> bool:
        return bool(self.frontmatter)

    @property
    def note_id(self) -> str:
        return str(self.frontmatter.get("id") or "")

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title") or "")


# -------------------------------------------------------------------
# Parsing
# -------------------------------------------------------------------

def parse_note(path: Path) -> ParsedNote:
    """Parse a single Markdown note. Never modifies the file."""
    try:
        raw_text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return ParsedNote(
            path=path,
            frontmatter={},
            body="",
            wikilinks=(),
            raw_text="",
            parse_errors=(f"Cannot read file: {exc}",),
        )

    frontmatter, body, errors = _split_frontmatter(raw_text)
    wikilinks = extract_wikilinks(body)

    return ParsedNote(
        path=path,
        frontmatter=frontmatter,
        body=body,
        wikilinks=wikilinks,
        raw_text=raw_text,
        parse_errors=tuple(errors),
    )


def _split_frontmatter(
    text: str,
) -> tuple[dict[str, Any], str, list[str]]:
    errors: list[str] = []
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text, []

    yaml_block = match.group(1)
    body = text[match.end():]

    try:
        parsed = yaml.safe_load(yaml_block)
    except yaml.YAMLError as exc:
        return {}, body, [f"Invalid YAML frontmatter: {exc}"]

    if not isinstance(parsed, dict):
        return {}, body, ["Frontmatter is not a YAML mapping."]

    return parsed, body, errors


def extract_wikilinks(text: str) -> tuple[str, ...]:
    """Extract all [[wikilink]] targets from text. Read-only."""
    seen: set[str] = set()
    result: list[str] = []
    for match in _WIKILINK_RE.finditer(text):
        target = match.group(1).strip()
        if target and target not in seen:
            result.append(target)
            seen.add(target)
    return tuple(result)


# -------------------------------------------------------------------
# Frontmatter → KnowledgeEntry conversion
# -------------------------------------------------------------------

def frontmatter_to_entry(
    fm: dict[str, Any],
) -> tuple[KnowledgeEntry | None, list[SchemaError]]:
    """Convert parsed frontmatter dict to a KnowledgeEntry.

    Returns (entry, errors). If conversion fails due to missing
    required enum values, entry is None and errors describe why.
    """
    errors: list[SchemaError] = []

    def _enum_or_error(
        enum_cls: type,
        value: Any,
        field_name: str,
    ) -> Any:
        try:
            return enum_cls(value)
        except (ValueError, KeyError):
            errors.append(SchemaError(
                field_name,
                f"Invalid value {value!r} for {enum_cls.__name__}.",
            ))
            return None

    entry_type = _enum_or_error(EntryType, fm.get("entry_type"), "entry_type")
    status = _enum_or_error(EntryStatus, fm.get("status"), "status")
    authority = _enum_or_error(
        AuthorityLabel, fm.get("authority_label"), "authority_label",
    )
    review_state = _enum_or_error(
        ReviewState, fm.get("review_state"), "review_state",
    )
    confidence = _enum_or_error(
        Confidence, fm.get("confidence"), "confidence",
    )

    if errors:
        return None, errors

    rels: list[Relationship] = []
    for raw_rel in (fm.get("relationships") or []):
        if not isinstance(raw_rel, dict):
            continue
        rel_type = _enum_or_error(
            RelationshipType, raw_rel.get("type"), "relationships[].type",
        )
        rel_conf = _enum_or_error(
            Confidence, raw_rel.get("confidence"), "relationships[].confidence",
        )
        if rel_type is None or rel_conf is None:
            continue
        rels.append(Relationship(
            type=rel_type,
            target=str(raw_rel.get("target") or ""),
            confidence=rel_conf,
            source_ref=str(raw_rel.get("source_ref") or ""),
            ledger_ref=str(raw_rel.get("ledger_ref") or ""),
            note=str(raw_rel.get("note") or ""),
        ))

    entry = KnowledgeEntry(
        id=str(fm.get("id") or ""),
        schema_version=int(fm.get("schema_version") or 0),
        title=str(fm.get("title") or ""),
        entry_type=entry_type,
        status=status,
        authority_label=authority,
        created_at=str(fm.get("created_at") or ""),
        updated_at=str(fm.get("updated_at") or ""),
        source_refs=tuple(fm.get("source_refs") or []),
        content_hash=str(fm.get("content_hash") or ""),
        review_state=review_state,
        confidence=confidence,
        project_scope=str(fm.get("project_scope") or ""),
        tags=tuple(fm.get("tags") or []),
        relationships=tuple(rels),
        supersedes=tuple(fm.get("supersedes") or []),
        superseded_by=tuple(fm.get("superseded_by") or []),
        ledger_refs=tuple(fm.get("ledger_refs") or []),
        reviewed_by=str(fm.get("reviewed_by") or ""),
        reviewed_at=str(fm.get("reviewed_at") or ""),
    )

    validation_errors = entry.validate()
    return entry, validation_errors
