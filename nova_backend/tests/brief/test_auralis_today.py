"""C1 Auralis Today — acceptance tests.

Verifies the five acceptance criteria from docs/design/AURALIS_TODAY_C1_DESIGN.md plus
determinism-across-reruns and the non-authorizing contract.
"""
from __future__ import annotations

from src.brief.auralis_today import (
    INPUTS_COMPLETE,
    INPUTS_PARTIAL,
    NOT_ENOUGH_TRUSTED_INPUTS,
    auralis_today_input_status,
    build_auralis_today_section,
)


def _shopify(**over):
    base = {
        "orders": {"order_count": 3},
        "products": {"active_products": 33},
        "order_split": {"public": 0, "proof": 1},
        "welcome10_uses": 0,
        "publication_counts": {"online_store": 33, "shop": 33, "google": 32},
        "top_margin_product": "Sun of Life sherpa",
    }
    base.update(over)
    return base


def _complete_inputs():
    return {
        "shopify": _shopify(),
        "decisions": [{"content": "order #1001 is family/proof", "tier": "locked"}],
        "owner_actions": [
            {"content": "Meta verification", "ownership": "needs_chris",
             "gates_revenue": True, "smallest_step": "open Business Suite, click Verify"},
            {"content": "July 9 Google review check", "ownership": "scheduled"},
        ],
        "promotion_queue": ["hooded sherpas", "tees", "hoodies"],
    }


# --- Criterion 1: one recommended action, no follow-up needed ---

def test_renders_exactly_five_lines_with_one_best_move():
    section = build_auralis_today_section(_complete_inputs())
    assert section.key == "auralis_today"
    assert len(section.items) == 5
    best = [i for i in section.items if i.startswith("Best move:")]
    assert len(best) == 1  # exactly one recommended action


def test_best_move_is_actionable_and_singular():
    section = build_auralis_today_section(_complete_inputs())
    best = next(i for i in section.items if i.startswith("Best move:"))
    # The revenue-gating blocker wins over the promotion queue.
    assert "Verify" in best


# --- Criterion 2: deterministic, same inputs -> same recommendation ---

def test_deterministic_across_reruns():
    inputs = _complete_inputs()
    first = build_auralis_today_section(inputs).items
    for _ in range(5):
        assert build_auralis_today_section(inputs).items == first


def test_promotion_queue_order_is_respected():
    inputs = _complete_inputs()
    inputs["owner_actions"] = [{"content": "x", "ownership": "scheduled"}]  # no blocker
    section = build_auralis_today_section(inputs)
    best = next(i for i in section.items if i.startswith("Best move:"))
    assert "hooded sherpas" in best  # top of the queue, deterministically


# --- Criterion 3: includes a "why this?" explanation ---

def test_best_move_includes_why():
    section = build_auralis_today_section(_complete_inputs())
    best = next(i for i in section.items if i.startswith("Best move:"))
    assert "—" in best  # reason clause present


# --- Criterion 4: explicit "not enough", never fabricates ---

def test_no_trusted_inputs_returns_not_enough_not_a_fabrication():
    section = build_auralis_today_section({})
    assert section.status == "not_configured"
    assert auralis_today_input_status({}) == NOT_ENOUGH_TRUSTED_INPUTS
    assert any("Not enough trusted inputs" in i for i in section.items)
    assert not any(i.startswith("Best move: promote") for i in section.items)


def test_shopify_down_degrades_revenue_line_without_fabricating():
    inputs = _complete_inputs()
    inputs["shopify"] = None  # Shopify unreachable, queue still present
    section = build_auralis_today_section(inputs)
    revenue = next(i for i in section.items if i.startswith("Revenue:"))
    assert "not enough" in revenue.lower()
    # A best move can still come from the (trusted) owner queue — that is not fabrication.
    assert len(section.items) == 5


def test_partial_inputs_do_not_invent_public_sales():
    inputs = _complete_inputs()
    inputs["shopify"] = {"orders": {"order_count": 5}, "products": {"active_products": 33}}
    section = build_auralis_today_section(inputs)
    revenue = next(i for i in section.items if i.startswith("Revenue:"))
    assert "public/proof split not available" in revenue
    assert "public sale" not in revenue  # never claims public sales it cannot prove


# --- Criterion 5: surface stays small ---

def test_surface_never_exceeds_five_lines():
    inputs = _complete_inputs()
    inputs["owner_actions"] += [
        {"content": f"extra {n}", "ownership": "needs_chris", "gates_revenue": True}
        for n in range(10)
    ]
    inputs["promotion_queue"] += [f"product {n}" for n in range(20)]
    assert len(build_auralis_today_section(inputs).items) == 5


# --- Input-status classification ---

def test_input_status_complete():
    assert auralis_today_input_status(_complete_inputs()) == INPUTS_COMPLETE


def test_input_status_partial_when_extensions_missing():
    inputs = _complete_inputs()
    inputs["shopify"] = {"orders": {"order_count": 3}, "products": {"active_products": 33}}
    assert auralis_today_input_status(inputs) == INPUTS_PARTIAL


def test_input_status_partial_when_only_queue_present():
    assert auralis_today_input_status(
        {"promotion_queue": ["hooded sherpas"]}
    ) == INPUTS_PARTIAL


# --- Non-authorizing contract ---

def test_section_is_read_only_shape():
    section = build_auralis_today_section(_complete_inputs())
    # AwarenessSection carries only display data — no command, no action, no capability id.
    d = section.to_dict()
    assert set(d.keys()) == {"key", "title", "items", "status", "source"}
    assert "command" not in d and "action" not in d
