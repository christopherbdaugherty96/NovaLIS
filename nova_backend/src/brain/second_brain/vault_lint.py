"""Read-only vault health and lint report.

Walks a vault directory, parses all .md files, and produces a
structured health report. Never modifies, repairs, or deletes files.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from src.brain.second_brain.frontmatter_parser import (
    ParsedNote,
    extract_wikilinks,
    frontmatter_to_entry,
    parse_note,
)
from src.brain.second_brain.schemas import KnowledgeEntry, SchemaError


class FindingSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class LintFinding:
    severity: FindingSeverity
    path: str
    rule: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity.value,
            "path": self.path,
            "rule": self.rule,
            "message": self.message,
        }


@dataclass(frozen=True)
class VaultHealthReport:
    vault_root: str
    total_notes: int
    parsed_ok: int
    with_frontmatter: int
    valid_entries: int
    total_wikilinks: int
    findings: tuple[LintFinding, ...]
    non_authorizing: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "non_authorizing", True)

    @property
    def error_count(self) -> int:
        return sum(
            1 for f in self.findings
            if f.severity == FindingSeverity.ERROR
        )

    @property
    def warning_count(self) -> int:
        return sum(
            1 for f in self.findings
            if f.severity == FindingSeverity.WARNING
        )

    @property
    def is_healthy(self) -> bool:
        return self.error_count == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "vault_root": self.vault_root,
            "total_notes": self.total_notes,
            "parsed_ok": self.parsed_ok,
            "with_frontmatter": self.with_frontmatter,
            "valid_entries": self.valid_entries,
            "total_wikilinks": self.total_wikilinks,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "is_healthy": self.is_healthy,
            "findings": [f.to_dict() for f in self.findings],
            "non_authorizing": True,
        }


def lint_vault(vault_root: Path) -> VaultHealthReport:
    """Run read-only lint over all .md files under vault_root.

    Never modifies files. Returns a VaultHealthReport.
    """
    if not vault_root.is_dir():
        return VaultHealthReport(
            vault_root=str(vault_root),
            total_notes=0,
            parsed_ok=0,
            with_frontmatter=0,
            valid_entries=0,
            total_wikilinks=0,
            findings=(LintFinding(
                severity=FindingSeverity.ERROR,
                path=str(vault_root),
                rule="vault_root_missing",
                message="Vault root directory does not exist.",
            ),),
        )

    md_files = sorted(vault_root.rglob("*.md"))
    findings: list[LintFinding] = []
    parsed_notes: list[ParsedNote] = []
    ids_seen: dict[str, str] = {}
    all_link_targets: set[str] = set()
    valid_entries: list[KnowledgeEntry] = []
    total_wikilinks = 0

    for md_path in md_files:
        if _is_excluded(md_path, vault_root):
            continue

        note = parse_note(md_path)
        parsed_notes.append(note)
        rel_path = str(md_path.relative_to(vault_root))

        for err in note.parse_errors:
            findings.append(LintFinding(
                severity=FindingSeverity.ERROR,
                path=rel_path,
                rule="parse_error",
                message=err,
            ))

        if not note.has_frontmatter:
            findings.append(LintFinding(
                severity=FindingSeverity.WARNING,
                path=rel_path,
                rule="missing_frontmatter",
                message="Note has no YAML frontmatter.",
            ))
            total_wikilinks += len(note.wikilinks)
            for link in note.wikilinks:
                all_link_targets.add(link)
            continue

        total_wikilinks += len(note.wikilinks)
        for link in note.wikilinks:
            all_link_targets.add(link)

        note_id = note.note_id
        if note_id:
            if note_id in ids_seen:
                findings.append(LintFinding(
                    severity=FindingSeverity.ERROR,
                    path=rel_path,
                    rule="duplicate_id",
                    message=(
                        f"Duplicate ID {note_id!r}, "
                        f"also in {ids_seen[note_id]}."
                    ),
                ))
            else:
                ids_seen[note_id] = rel_path

        entry, schema_errors = frontmatter_to_entry(note.frontmatter)
        for err in schema_errors:
            findings.append(LintFinding(
                severity=FindingSeverity.ERROR,
                path=rel_path,
                rule=f"schema_{err.field}",
                message=err.message,
            ))

        if entry is not None and not schema_errors:
            valid_entries.append(entry)

    _check_broken_wikilinks(
        parsed_notes, all_link_targets, ids_seen,
        vault_root, findings,
    )
    _check_missing_relationship_targets(valid_entries, ids_seen, findings)

    return VaultHealthReport(
        vault_root=str(vault_root),
        total_notes=len(parsed_notes),
        parsed_ok=sum(1 for n in parsed_notes if not n.parse_errors),
        with_frontmatter=sum(1 for n in parsed_notes if n.has_frontmatter),
        valid_entries=len(valid_entries),
        total_wikilinks=total_wikilinks,
        findings=tuple(findings),
    )


def _is_excluded(path: Path, vault_root: Path) -> bool:
    rel = path.relative_to(vault_root)
    parts = rel.parts
    if any(p.startswith(".") for p in parts):
        return True
    if any(p.lower() in ("templates", "raw") for p in parts[:-1]):
        return True
    return False


def _check_broken_wikilinks(
    notes: list[ParsedNote],
    all_link_targets: set[str],
    ids_seen: dict[str, str],
    vault_root: Path,
    findings: list[LintFinding],
) -> None:
    note_stems: set[str] = set()
    for note in notes:
        note_stems.add(note.path.stem)
        if note.note_id:
            note_stems.add(note.note_id)

    for target in sorted(all_link_targets):
        if target in note_stems:
            continue
        if target in ids_seen:
            continue
        for note in notes:
            if target in note.wikilinks:
                rel_path = str(note.path.relative_to(vault_root))
                findings.append(LintFinding(
                    severity=FindingSeverity.WARNING,
                    path=rel_path,
                    rule="broken_wikilink",
                    message=f"Wikilink target [[{target}]] not found in vault.",
                ))
                break


def _check_missing_relationship_targets(
    entries: list[KnowledgeEntry],
    ids_seen: dict[str, str],
    findings: list[LintFinding],
) -> None:
    for entry in entries:
        for rel in entry.relationships:
            if rel.target not in ids_seen:
                path = ids_seen.get(entry.id, entry.id)
                findings.append(LintFinding(
                    severity=FindingSeverity.WARNING,
                    path=path,
                    rule="missing_relationship_target",
                    message=(
                        f"Relationship target {rel.target!r} "
                        f"not found in vault."
                    ),
                ))
