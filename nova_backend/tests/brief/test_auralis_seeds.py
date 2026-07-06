"""C1 Auralis Today — governed-memory seed loader tests (pure, no store coupling)."""
from __future__ import annotations

from src.brief.auralis_seeds import build_auralis_inputs_from_memory
from src.brief.auralis_today import build_auralis_today_section


def _items():
    return [
        {"title": "order #1001 is family/proof", "content": "custom order, not public demand",
         "tier": "locked", "tags": ["decision"]},
        {"title": "Meta verification", "content": "open Business Suite, click Verify",
         "tags": ["needs_chris", "gates_revenue"]},
        {"title": "July 9 Google review check", "content": "automation checks results",
         "tags": ["scheduled"]},
        {"title": "promotion", "content": "hooded sherpas\ntees\nhoodies",
         "tags": ["promotion_queue"]},
    ]


def test_classifies_each_seed_type():
    inputs = build_auralis_inputs_from_memory(_items())
    assert [d["content"] for d in inputs["decisions"]] == ["custom order, not public demand"]
    assert inputs["promotion_queue"] == ["hooded sherpas", "tees", "hoodies"]
    owners = {a["ownership"] for a in inputs["owner_actions"]}
    assert owners == {"needs_chris", "scheduled"}


def test_gates_revenue_flag_and_smallest_step():
    inputs = build_auralis_inputs_from_memory(_items())
    meta = next(a for a in inputs["owner_actions"] if a["content"] == "Meta verification")
    assert meta["gates_revenue"] is True
    assert meta["smallest_step"] == "open Business Suite, click Verify"


def test_ordering_is_deterministic_regardless_of_input_order():
    import random
    items = _items()
    shuffled = items[:]
    random.Random(1).shuffle(shuffled)
    a = build_auralis_inputs_from_memory(items)["owner_actions"]
    b = build_auralis_inputs_from_memory(shuffled)["owner_actions"]
    assert a == b  # gating-first, then rank, then content — stable


def test_promotion_list_accepts_comma_separated():
    items = [{"title": "promotion", "content": "a, b, c", "tags": ["promotion_queue"]}]
    assert build_auralis_inputs_from_memory(items)["promotion_queue"] == ["a", "b", "c"]


def test_seeds_feed_a_renderable_section():
    inputs = build_auralis_inputs_from_memory(_items(), shopify_snapshot={
        "orders": {"order_count": 1},
        "products": {"active_products": 33},
        "order_split": {"public": 0, "proof": 1},
    })
    section = build_auralis_today_section(inputs)
    assert section.status == "ok"
    assert len(section.items) == 5
    best = next(i for i in section.items if i.startswith("Best move:"))
    assert "Verify" in best  # gating blocker wins deterministically


def test_store_shaped_items_use_body_for_smallest_step():
    items = [
        {
            "title": "Auralis-Digital repo exposure",
            "body": "migrate hosting, then flip repo private",
            "tier": "active",
            "tags": ["needs_chris", "gates_revenue"],
            "links": {"project_thread_name": "auralis", "project_thread_key": "auralis"},
        }
    ]
    inputs = build_auralis_inputs_from_memory(items)
    section = build_auralis_today_section(inputs)
    best = next(i for i in section.items if i.startswith("Best move:"))
    assert "migrate hosting, then flip repo private" in best


def test_empty_memory_yields_no_fabrication():
    inputs = build_auralis_inputs_from_memory([], shopify_snapshot=None)
    section = build_auralis_today_section(inputs)
    assert section.status == "not_configured"
    assert not any(i.startswith("Best move: promote") for i in section.items)
