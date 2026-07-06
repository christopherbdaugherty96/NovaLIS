"""C1 wiring — Auralis Today appears in the brief only when inputs are supplied."""
from __future__ import annotations

from src.brief.awareness_brief import compose_awareness_brief


def _auralis_inputs():
    return {
        "shopify": {"orders": {"order_count": 1}, "products": {"active_products": 33},
                    "order_split": {"public": 0, "proof": 1}},
        "owner_actions": [{"content": "Meta verification", "ownership": "needs_chris",
                           "gates_revenue": True, "smallest_step": "click Verify"}],
        "promotion_queue": ["hooded sherpas"],
    }


def test_default_composition_unchanged_seven_sections():
    brief = compose_awareness_brief()
    assert len(brief.sections) == 7
    assert brief.to_dict()["total_count"] == 7
    assert "auralis_today" not in {s.key for s in brief.sections}


def test_auralis_section_appended_when_inputs_supplied():
    brief = compose_awareness_brief(auralis_inputs=_auralis_inputs())
    assert len(brief.sections) == 8
    keys = {s.key for s in brief.sections}
    assert "auralis_today" in keys
    auralis = next(s for s in brief.sections if s.key == "auralis_today")
    assert len(auralis.items) == 5


def test_auralis_inputs_none_is_the_default_path():
    assert len(compose_awareness_brief(auralis_inputs=None).sections) == 7
