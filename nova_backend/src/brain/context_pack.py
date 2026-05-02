"""Context Pack — bounded, labeled context bridge between Memory/Search/Project and Brain.

Responsibilities:
  - Select relevant context items from memory and other sources
  - Label every item with source_label and authority_label
  - Enforce char budgets — drop memory items when budget exhausted
  - Truncate runtime truth items to fit rather than dropping them
  - Surface stale/conflict/budget warnings
  - Explain why each item was selected (why_selected)
  - Sort by authority: runtime_truth first, then confirmed, then candidate

Non-responsibilities:
  - Must not authorize action
  - Must not treat candidate items as confirmed
  - Must not override runtime truth with memory
  - Must not silently hide conflicts or budget overruns

Non-authorizing frozen dataclass:
  execution_performed=False and authorization_granted=False are enforced
  in __post_init__ and cannot be set by callers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Source labels  (matches CONTEXT_PACK_SPEC.md)
# ---------------------------------------------------------------------------

SOURCE_RUNTIME_TRUTH = "runtime_truth"
SOURCE_CURRENT_CONVERSATION = "current_conversation"
SOURCE_CONFIRMED_MEMORY = "confirmed_memory"
SOURCE_CANDIDATE_MEMORY = "candidate_memory"
SOURCE_SEARCH_EVIDENCE = "search_evidence"
SOURCE_RECEIPT = "receipt"
SOURCE_ASSUMPTION = "assumption"

# ---------------------------------------------------------------------------
# Authority labels  (matches CONTEXT_PACK_SPEC.md)
# ---------------------------------------------------------------------------

AUTHORITY_RUNTIME_TRUTH = "runtime_truth"
AUTHORITY_CONFIRMED_PROJECT_MEMORY = "confirmed_project_memory"
AUTHORITY_CANDIDATE_MEMORY = "candidate_memory"
AUTHORITY_ASSUMPTION = "assumption"

# Ordered from highest to lowest — used for sort key and budget priority
_AUTHORITY_RANK: dict[str, int] = {
    AUTHORITY_RUNTIME_TRUTH: 0,
    AUTHORITY_CONFIRMED_PROJECT_MEMORY: 1,
    AUTHORITY_CANDIDATE_MEMORY: 2,
    AUTHORITY_ASSUMPTION: 3,
}

# ---------------------------------------------------------------------------
# Warning types  (matches CONTEXT_PACK_SPEC.md)
# ---------------------------------------------------------------------------

WARN_STALE_MEMORY = "stale_memory"
WARN_CONFLICTING_SOURCES = "conflicting_sources"
WARN_BUDGET_EXCEEDED = "budget_exceeded"
WARN_RUNTIME_TRUTH_UNKNOWN = "runtime_truth_unknown"
WARN_WEAK_SEARCH_EVIDENCE = "weak_search_evidence"
WARN_TOO_MANY_WARNINGS = "too_many_warnings"

# ---------------------------------------------------------------------------
# Budget defaults  (matches CONTEXT_PACK_SPEC.md)
# ---------------------------------------------------------------------------

DEFAULT_BUDGET_CHARS = 4000
DEFAULT_MAX_CONFIRMED = 5
DEFAULT_MAX_CANDIDATE = 2
DEFAULT_MAX_WARNINGS = 2
DEFAULT_STALE_DAYS = 30


# ---------------------------------------------------------------------------
# ContextItem
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ContextItem:
    """A single item selected for the context pack."""

    id: str
    title: str
    content: str
    source_label: str     # one of SOURCE_* constants
    authority_label: str  # one of AUTHORITY_* constants
    why_selected: str
    scope: str = ""
    thread_name: str = ""
    is_stale: bool = False
    stale_reason: str = ""

    @property
    def char_count(self) -> int:
        return len(self.content)

    @property
    def authority_rank(self) -> int:
        return _AUTHORITY_RANK.get(self.authority_label, 99)

    @property
    def is_candidate(self) -> bool:
        return self.authority_label == AUTHORITY_CANDIDATE_MEMORY

    @property
    def is_runtime_truth(self) -> bool:
        return self.authority_label == AUTHORITY_RUNTIME_TRUTH

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "source_label": self.source_label,
            "authority_label": self.authority_label,
            "why_selected": self.why_selected,
            "scope": self.scope,
            "thread_name": self.thread_name,
            "char_count": self.char_count,
            "is_candidate": self.is_candidate,
            "is_runtime_truth": self.is_runtime_truth,
            "is_stale": self.is_stale,
            "stale_reason": self.stale_reason,
        }


# ---------------------------------------------------------------------------
# ContextPackWarning
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ContextPackWarning:
    """A warning surfaced during context pack composition."""

    warning_type: str  # one of WARN_* constants
    item_id: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "warning_type": self.warning_type,
            "item_id": self.item_id,
            "reason": self.reason,
        }


# ---------------------------------------------------------------------------
# ContextPack
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ContextPack:
    """Bounded, labeled context bridge between Memory/Search/Project and Brain.

    Non-authorizing: execution_performed and authorization_granted are always
    False and enforced in __post_init__.
    """

    items: tuple[ContextItem, ...]
    warnings: tuple[ContextPackWarning, ...]
    budget_used: int
    budget_limit: int
    composed_at: str

    # Non-authorizing invariants — callers cannot override these
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "execution_performed", False)
        object.__setattr__(self, "authorization_granted", False)

    # ------------------------------------------------------------------
    # Derived views
    # ------------------------------------------------------------------

    @property
    def candidate_items(self) -> tuple[ContextItem, ...]:
        return tuple(i for i in self.items if i.is_candidate)

    @property
    def runtime_truth_items(self) -> tuple[ContextItem, ...]:
        return tuple(i for i in self.items if i.is_runtime_truth)

    @property
    def confirmed_items(self) -> tuple[ContextItem, ...]:
        return tuple(
            i for i in self.items
            if i.authority_label == AUTHORITY_CONFIRMED_PROJECT_MEMORY
        )

    @property
    def stale_items(self) -> tuple[ContextItem, ...]:
        return tuple(i for i in self.items if i.is_stale)

    @property
    def budget_remaining(self) -> int:
        return max(0, self.budget_limit - self.budget_used)

    @property
    def within_budget(self) -> bool:
        return self.budget_used <= self.budget_limit

    @property
    def candidate_count(self) -> int:
        return len(self.candidate_items)

    @property
    def runtime_truth_count(self) -> int:
        return len(self.runtime_truth_items)

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": [i.to_dict() for i in self.items],
            "warnings": [w.to_dict() for w in self.warnings],
            "budget_used": self.budget_used,
            "budget_limit": self.budget_limit,
            "budget_remaining": self.budget_remaining,
            "within_budget": self.within_budget,
            "candidate_count": self.candidate_count,
            "runtime_truth_count": self.runtime_truth_count,
            "composed_at": self.composed_at,
            "execution_performed": self.execution_performed,
            "authorization_granted": self.authorization_granted,
        }

    def to_legacy_format(self) -> list[dict[str, str]]:
        """Return items in the format expected by _select_relevant_memory_context.

        Allows drop-in use alongside existing brain_server.py code.
        """
        return [
            {
                "id": i.id,
                "title": i.title,
                "content": i.content,
                "scope": i.scope,
                "thread_name": i.thread_name,
                "source": i.source_label,
                "authority_label": i.authority_label,
                "why_selected": i.why_selected,
            }
            for i in self.items
        ]

    def render_context_block(self, *, mark_candidates: bool = True) -> str:
        """Render items as a compact prompt block for injection.

        - Items are listed in authority order (runtime_truth first).
        - Candidate items are flagged so the Brain can treat them appropriately.
        - Stale items are noted.
        - Warnings are appended at the end.
        """
        if not self.items:
            return ""

        parts: list[str] = []
        for item in self.items:
            label = f"[{item.authority_label}]"
            flags: list[str] = []
            if mark_candidates and item.is_candidate:
                flags.append("unconfirmed — treat as suggestion only")
            if item.is_stale:
                flags.append(f"may be stale: {item.stale_reason}" if item.stale_reason else "may be stale")
            if flags:
                label += f" ({'; '.join(flags)})"
            parts.append(f"{label} {item.title}: {item.content}")

        block = "\n".join(parts)
        if self.warnings:
            warn_lines = [f"  - [{w.warning_type}] {w.reason}" for w in self.warnings]
            block += "\n[context warnings]\n" + "\n".join(warn_lines)
        return block


# ---------------------------------------------------------------------------
# compose_context_pack
# ---------------------------------------------------------------------------

def compose_context_pack(
    query: str,
    *,
    memory_items: list[dict[str, Any]] | None = None,
    runtime_truth_items: list[dict[str, Any]] | None = None,
    budget_chars: int = DEFAULT_BUDGET_CHARS,
    max_confirmed: int = DEFAULT_MAX_CONFIRMED,
    max_candidate: int = DEFAULT_MAX_CANDIDATE,
    max_warnings: int = DEFAULT_MAX_WARNINGS,
    stale_threshold_days: int = DEFAULT_STALE_DAYS,
) -> ContextPack:
    """Compose a bounded, labeled context pack for the given query.

    Priority order:
      1. Runtime truth items — truncated to fit budget, never dropped
      2. Confirmed memory items (source: explicit_user_save or explicit_user_edit)
      3. Candidate memory items (source: auto_extracted, observed, or unknown)

    Budget enforcement:
      - Runtime truth items are truncated at budget_chars if too large.
      - Memory items that exceed the remaining budget are dropped with a warning.
      - Confirmed items are always preferred over candidates when budget is tight.

    Stale detection:
      - Items with updated_at or created_at older than stale_threshold_days days
        are flagged with is_stale=True and a stale_memory warning.

    Conflict detection:
      - Items with identical title prefixes (first 40 chars) get a
        conflicting_sources warning.

    Returns a frozen ContextPack with execution_performed=False and
    authorization_granted=False enforced in __post_init__.
    """
    composed_at = datetime.now(timezone.utc).isoformat()
    budget_remaining = max(0, budget_chars)
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=max(0, stale_threshold_days))

    selected: list[ContextItem] = []
    raw_warnings: list[ContextPackWarning] = []

    # -- Step 1: Runtime truth items — truncate to fit, never drop ----------
    for rt in list(runtime_truth_items or []):
        content = str(rt.get("content") or rt.get("body") or "").strip()
        if not content:
            continue
        # Truncate to budget if needed — runtime truth stays, just smaller
        if len(content) > budget_remaining and budget_remaining > 0:
            content = content[:budget_remaining]
        elif budget_remaining <= 0:
            content = content[:200]  # minimal excerpt to remain useful
        item = ContextItem(
            id=str(rt.get("id") or ""),
            title=str(rt.get("title") or "").strip(),
            content=content,
            source_label=SOURCE_RUNTIME_TRUTH,
            authority_label=AUTHORITY_RUNTIME_TRUTH,
            why_selected="runtime truth — highest authority",
            scope=str(rt.get("scope") or ""),
        )
        budget_remaining = max(0, budget_remaining - item.char_count)
        selected.append(item)

    # -- Step 2: Classify memory items into confirmed vs candidate ----------
    confirmed: list[ContextItem] = []
    candidate: list[ContextItem] = []

    for mem in list(memory_items or []):
        # Skip deleted items defensively
        if bool(mem.get("deleted")):
            continue
        content = str(
            mem.get("content") or mem.get("body") or mem.get("content_raw") or ""
        ).strip()
        if not content:
            continue

        source = str(mem.get("source") or "").strip()
        is_explicit = source in {"explicit_user_save", "explicit_user_edit"}
        if is_explicit:
            authority = AUTHORITY_CONFIRMED_PROJECT_MEMORY
            source_label = SOURCE_CONFIRMED_MEMORY
            why = f"confirmed by user (source: {source})"
        else:
            authority = AUTHORITY_CANDIDATE_MEMORY
            source_label = SOURCE_CANDIDATE_MEMORY
            why = f"auto-extracted — treat as suggestion only (source: {source or 'unknown'})"

        # Stale check
        is_stale = False
        stale_reason = ""
        ts_str = str(mem.get("updated_at") or mem.get("created_at") or "").strip()
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts < stale_cutoff:
                    is_stale = True
                    age_days = (now - ts).days
                    stale_reason = f"last updated {age_days} days ago"
            except (ValueError, TypeError):
                pass

        item = ContextItem(
            id=str(mem.get("id") or ""),
            title=str(mem.get("title") or "").strip(),
            content=content,
            source_label=source_label,
            authority_label=authority,
            why_selected=why,
            scope=str(mem.get("scope") or ""),
            thread_name=str(mem.get("thread_name") or ""),
            is_stale=is_stale,
            stale_reason=stale_reason,
        )
        if authority == AUTHORITY_CONFIRMED_PROJECT_MEMORY:
            confirmed.append(item)
        else:
            candidate.append(item)

    # -- Step 3: Add confirmed items up to max_confirmed and budget ----------
    for item in confirmed[:max_confirmed]:
        if item.char_count > budget_remaining:
            raw_warnings.append(ContextPackWarning(
                warning_type=WARN_BUDGET_EXCEEDED,
                item_id=item.id,
                reason=f"Confirmed memory '{item.title[:40]}' dropped — budget exhausted.",
            ))
            continue
        budget_remaining = max(0, budget_remaining - item.char_count)
        selected.append(item)
        if item.is_stale:
            raw_warnings.append(ContextPackWarning(
                warning_type=WARN_STALE_MEMORY,
                item_id=item.id,
                reason=f"Memory '{item.title[:40]}' may be outdated — {item.stale_reason}.",
            ))

    if len(confirmed) > max_confirmed:
        raw_warnings.append(ContextPackWarning(
            warning_type=WARN_BUDGET_EXCEEDED,
            item_id="",
            reason=f"{len(confirmed) - max_confirmed} confirmed item(s) omitted — max_confirmed limit.",
        ))

    # -- Step 4: Add candidate items up to max_candidate and budget ----------
    for item in candidate[:max_candidate]:
        if item.char_count > budget_remaining:
            raw_warnings.append(ContextPackWarning(
                warning_type=WARN_BUDGET_EXCEEDED,
                item_id=item.id,
                reason=f"Candidate memory '{item.title[:40]}' dropped — budget exhausted.",
            ))
            continue
        budget_remaining = max(0, budget_remaining - item.char_count)
        selected.append(item)
        if item.is_stale:
            raw_warnings.append(ContextPackWarning(
                warning_type=WARN_STALE_MEMORY,
                item_id=item.id,
                reason=f"Candidate '{item.title[:40]}' may be outdated — {item.stale_reason}.",
            ))

    if len(candidate) > max_candidate:
        raw_warnings.append(ContextPackWarning(
            warning_type=WARN_BUDGET_EXCEEDED,
            item_id="",
            reason=f"{len(candidate) - max_candidate} candidate item(s) omitted — max_candidate limit.",
        ))

    # -- Step 5: Conflict detection — same title prefix ----------------------
    seen_prefixes: dict[str, str] = {}
    for item in selected:
        prefix = item.title[:40].lower().strip()
        if not prefix:
            continue
        if prefix in seen_prefixes:
            raw_warnings.append(ContextPackWarning(
                warning_type=WARN_CONFLICTING_SOURCES,
                item_id=item.id,
                reason=(
                    f"'{item.title[:40]}' may conflict with earlier item "
                    f"'{seen_prefixes[prefix][:40]}' — verify which is current."
                ),
            ))
        else:
            seen_prefixes[prefix] = item.title

    # -- Step 6: Sort by authority rank so runtime_truth is first -----------
    selected.sort(key=lambda i: i.authority_rank)

    # -- Step 7: Cap warnings at max_warnings --------------------------------
    final_warnings: tuple[ContextPackWarning, ...]
    if len(raw_warnings) > max_warnings:
        kept = raw_warnings[:max_warnings]
        overflow = len(raw_warnings) - max_warnings
        kept.append(ContextPackWarning(
            warning_type=WARN_TOO_MANY_WARNINGS,
            item_id="",
            reason=f"{overflow} additional warning(s) suppressed — see full context for details.",
        ))
        final_warnings = tuple(kept)
    else:
        final_warnings = tuple(raw_warnings)

    budget_used = max(0, budget_chars - budget_remaining)

    return ContextPack(
        items=tuple(selected),
        warnings=final_warnings,
        budget_used=budget_used,
        budget_limit=budget_chars,
        composed_at=composed_at,
    )
