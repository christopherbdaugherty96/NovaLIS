"""Auralis Today — C1 business decision surface for the Daily Awareness Brief.

One five-line section that answers a single question: what is the best move today for the
Auralis / Lucid Creations business? A decision surface, not a dashboard.

Design: docs/design/AURALIS_TODAY_C1_DESIGN.md

Invariants:
  - Read-only. No writes, no new capability, no network of its own (consumes a snapshot
    already fetched by the governed cap-65 read path).
  - Deterministic. Same inputs -> same recommendation. No LLM calls, no randomness.
  - Honest. When trusted inputs are missing it says so explicitly and never fabricates a
    recommendation.

Trusted inputs (and nothing else):
  - shopify: read-only store snapshot dict (cap 65), optionally with C1 extensions
    order_split {public, proof}, welcome10_uses, publication_counts.
  - decisions: settled decisions (locked governed-memory items).
  - owner_actions: items tagged needs_chris / agent_doable / scheduled / blocked, each may
    carry gates_revenue (bool) and smallest_step (str).
  - promotion_queue: ordered list of product names (static, from governed memory).
"""

from __future__ import annotations

from typing import Any

from src.brief.awareness_brief import AwarenessSection

# Input-status values (internal; makes the honesty rule testable).
INPUTS_COMPLETE = "inputs_complete"
INPUTS_PARTIAL = "inputs_partial"
NOT_ENOUGH_TRUSTED_INPUTS = "not_enough_trusted_inputs"

OWNER_BLOCKER_PREFIX = "Owner blocker:"
BEST_MOVE_PREFIX = "Best move:"
DECISION_ITEM_PREFIXES = (OWNER_BLOCKER_PREFIX, BEST_MOVE_PREFIX)

_MAX_LEN = 160
_NO_RECOMMENDATION = "not enough trusted inputs to recommend today"


def _clean(value: Any, *, limit: int = _MAX_LEN) -> str:
    return str(value or "").strip()[:limit]


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _has_revenue_signal(shopify: Any) -> bool:
    return isinstance(shopify, dict) and isinstance(shopify.get("orders"), dict)


def _has_queue_signal(owner_actions: list[Any], promotion_queue: list[Any]) -> bool:
    return bool(owner_actions) or bool(promotion_queue)


def auralis_today_input_status(inputs: dict[str, Any] | None) -> str:
    """Classify trusted-input completeness. Pure; called by the builder and by tests.

    complete  -> Shopify snapshot WITH the C1 extensions, plus an owner-action queue and a
                 promotion queue.
    partial   -> at least one trusted signal present, but not the full set.
    not_enough -> no trusted revenue signal and no queue signal: cannot recommend.
    """
    inputs = inputs or {}
    shopify = inputs.get("shopify")
    owner_actions = _as_list(inputs.get("owner_actions"))
    promotion_queue = _as_list(inputs.get("promotion_queue"))

    revenue = _has_revenue_signal(shopify)
    queue = _has_queue_signal(owner_actions, promotion_queue)

    if not revenue and not queue:
        return NOT_ENOUGH_TRUSTED_INPUTS

    extensions_present = revenue and isinstance(shopify, dict) and (
        "order_split" in shopify or "welcome10_uses" in shopify or "publication_counts" in shopify
    )
    if revenue and extensions_present and owner_actions and promotion_queue:
        return INPUTS_COMPLETE
    return INPUTS_PARTIAL


def _status_line(shopify: Any, owner_actions: list[dict[str, Any]]) -> str:
    if not isinstance(shopify, dict) or not shopify:
        return "Store status unavailable (Shopify not connected)."
    parts: list[str] = []
    products = shopify.get("products")
    if isinstance(products, dict):
        active = products.get("active_products")
        if active is not None:
            parts.append(f"{active} active products")
    pubs = shopify.get("publication_counts")
    if isinstance(pubs, dict) and pubs:
        live = sum(1 for v in pubs.values() if isinstance(v, int) and v > 0)
        parts.append(f"{live} channels live")
    blockers = [a for a in owner_actions if a.get("ownership") in {"needs_chris", "blocked"}]
    if blockers:
        parts.append(f"{len(blockers)} owner blocker{'s' if len(blockers) != 1 else ''}")
    return "Store live. " + ", ".join(parts) + "." if parts else "Store live."


def _revenue_line(shopify: Any) -> str:
    if not _has_revenue_signal(shopify):
        return f"Revenue: {_NO_RECOMMENDATION} (Shopify unavailable)."
    split = shopify.get("order_split")
    if isinstance(split, dict) and ("public" in split or "proof" in split):
        public = int(split.get("public") or 0)
        proof = int(split.get("proof") or 0)
        seg = f"{public} public sale{'s' if public != 1 else ''}, {proof} family/proof"
    else:
        # No tag split extension yet: report totals honestly, do not infer public sales.
        count = int((shopify.get("orders") or {}).get("order_count") or 0)
        seg = f"{count} orders (public/proof split not available)"
    extras: list[str] = []
    uses = shopify.get("welcome10_uses")
    if isinstance(uses, int):
        extras.append(f"WELCOME10 x{uses}")
    top = _clean(shopify.get("top_margin_product"), limit=40)
    if top:
        extras.append(f"top margin: {top}")
    tail = (" | " + " | ".join(extras)) if extras else ""
    return f"Revenue: {seg}{tail}."


def _top_blocker(owner_actions: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The single revenue-gating owner blocker, deterministically chosen.

    Order: revenue-gating needs_chris/blocked items first, ties broken by list order
    (the caller supplies a stable, intentionally-ordered queue).
    """
    gating = [
        a for a in owner_actions
        if a.get("ownership") in {"needs_chris", "blocked"} and a.get("gates_revenue")
    ]
    return gating[0] if gating else None


def _owner_blocker_line(blocker: dict[str, Any] | None) -> str:
    if not blocker:
        return f"{OWNER_BLOCKER_PREFIX} none gating revenue right now."
    return f"{OWNER_BLOCKER_PREFIX} {_clean(blocker.get('content'), limit=120)}"


def _best_move(
    blocker: dict[str, Any] | None,
    promotion_queue: list[Any],
    status: str,
) -> str:
    """Deterministic. Blocker-that-gates-revenue wins; else top of the promotion queue."""
    if blocker:
        step = _clean(blocker.get("smallest_step") or blocker.get("content"), limit=120)
        return f"{BEST_MOVE_PREFIX} {step} - it gates revenue and only you can do it."
    if promotion_queue:
        top = _clean(promotion_queue[0], limit=80)
        return f"{BEST_MOVE_PREFIX} promote {top} - top of the promotion queue, channels ready."
    return f"{BEST_MOVE_PREFIX} {_NO_RECOMMENDATION}."


def _watch_line(owner_actions: list[dict[str, Any]]) -> str:
    scheduled = [a for a in owner_actions if a.get("ownership") == "scheduled"]
    if not scheduled:
        return "Watch: nothing scheduled."
    return f"Watch: {_clean(scheduled[0].get('content'), limit=120)}"


def build_auralis_today_section(inputs: dict[str, Any] | None) -> AwarenessSection:
    """Build the five-line Auralis Today section. Read-only, deterministic, non-authorizing."""
    inputs = inputs or {}
    status = auralis_today_input_status(inputs)

    if status == NOT_ENOUGH_TRUSTED_INPUTS:
        return AwarenessSection(
            key="auralis_today",
            title="Auralis Today",
            items=(
                "Not enough trusted inputs to recommend today.",
                "Connect Shopify (read-only) or seed owner-action/promotion items.",
            ),
            status="not_configured",
            source=f"auralis:{status}",
        )

    shopify = inputs.get("shopify")
    owner_actions = [a for a in _as_list(inputs.get("owner_actions")) if isinstance(a, dict)]
    promotion_queue = _as_list(inputs.get("promotion_queue"))

    blocker = _top_blocker(owner_actions)
    items = (
        _status_line(shopify, owner_actions),
        _revenue_line(shopify),
        _owner_blocker_line(blocker),
        _best_move(blocker, promotion_queue, status),
        _watch_line(owner_actions),
    )
    return AwarenessSection(
        key="auralis_today",
        title="Auralis Today",
        items=items,
        status="ok",
        source=f"auralis:{status}",
    )
