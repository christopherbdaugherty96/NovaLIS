"""Auralis Today — governed-memory seed loader (pure, read-only).

Translates governed-memory items (from GovernedMemoryStore.list_items) into the trusted
input set consumed by build_auralis_today_section. No writes, no store coupling: the caller
supplies the raw item list, this module classifies it deterministically.

Seed conventions (thread_name="auralis"):
  - Decision: tier="locked" or tag "decision". content (or title) is the decision text.
  - Owner action: exactly one ownership tag in {needs_chris, agent_doable, scheduled, blocked}.
    title = the action; content = the smallest next step; tag "gates_revenue" flags it.
  - Promotion queue: a single item tagged "promotion_queue"; its content lines (or
    comma-separated values) are the ordered product list.
"""

from __future__ import annotations

from typing import Any

_OWNERSHIP_TAGS = ("blocked", "needs_chris", "scheduled", "agent_doable")
_OWNERSHIP_RANK = {tag: i for i, tag in enumerate(_OWNERSHIP_TAGS)}


def _tags(item: dict[str, Any]) -> set[str]:
    return {str(t).strip().lower() for t in (item.get("tags") or []) if str(t).strip()}


def _text(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        val = str(item.get(key) or "").strip()
        if val:
            return val
    return ""


def _parse_promotion_list(content: str) -> list[str]:
    raw = content.replace(",", "\n")
    return [line.strip() for line in raw.splitlines() if line.strip()]


def build_auralis_inputs_from_memory(
    items: list[dict[str, Any]] | None,
    shopify_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify governed-memory items into the C1 trusted input set. Deterministic."""
    decisions: list[dict[str, Any]] = []
    owner_actions: list[dict[str, Any]] = []
    promotion_queue: list[str] = []

    for item in items or []:
        if not isinstance(item, dict):
            continue
        tags = _tags(item)
        tier = str(item.get("tier") or "").strip().lower()

        if "promotion_queue" in tags:
            promotion_queue = _parse_promotion_list(_text(item, "content", "title"))
            continue

        ownership = next((t for t in _OWNERSHIP_TAGS if t in tags), "")
        if ownership:
            owner_actions.append({
                "content": _text(item, "title", "content"),
                "ownership": ownership,
                "gates_revenue": "gates_revenue" in tags,
                "smallest_step": _text(item, "content", "title"),
            })
            continue

        if tier == "locked" or "decision" in tags:
            decisions.append({"content": _text(item, "content", "title"), "tier": "locked"})

    # Deterministic ordering independent of memory's updated_at sort:
    # gating actions first, then by ownership rank, then by content.
    owner_actions.sort(key=lambda a: (
        not a.get("gates_revenue"),
        _OWNERSHIP_RANK.get(a.get("ownership", ""), 99),
        a.get("content", ""),
    ))

    return {
        "shopify": shopify_snapshot,
        "decisions": decisions,
        "owner_actions": owner_actions,
        "promotion_queue": promotion_queue,
    }
