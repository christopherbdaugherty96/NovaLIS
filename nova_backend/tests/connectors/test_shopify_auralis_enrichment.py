"""C1 Shopify enrichment parsers — tested against mock GraphQL fragments (no network)."""
from __future__ import annotations

from src.connectors.shopify_auralis_enrichment import (
    parse_enrichment,
    parse_order_split,
    parse_publication_counts,
    parse_welcome10_uses,
)


def test_order_split_tags_family_as_proof_untagged_as_public():
    edges = [
        {"node": {"tags": ["family"]}},
        {"node": {"tags": []}},
        {"node": {"tags": ["Custom", "vip"]}},
        {"node": {"tags": ["repeat"]}},
    ]
    assert parse_order_split(edges) == {"public": 2, "proof": 2}


def test_order_split_empty_is_zero_zero_not_error():
    assert parse_order_split([]) == {"public": 0, "proof": 0}
    assert parse_order_split(None) == {"public": 0, "proof": 0}


def test_welcome10_sums_usage_case_insensitive():
    edges = [
        {"node": {"codeDiscount": {
            "codes": {"edges": [{"node": {"code": "welcome10"}}]}, "asyncUsageCount": 4}}},
        {"node": {"codeDiscount": {
            "codes": {"edges": [{"node": {"code": "SUMMER"}}]}, "asyncUsageCount": 9}}},
    ]
    assert parse_welcome10_uses(edges) == 4


def test_welcome10_zero_when_absent():
    assert parse_welcome10_uses([]) == 0
    assert parse_welcome10_uses([{"node": {"codeDiscount": {}}}]) == 0


def test_publication_counts_records_named_channels():
    edges = [{"node": {"name": "Online Store"}}, {"node": {"name": "Shop"}}, {"node": {"name": ""}}]
    assert parse_publication_counts(edges) == {"Online Store": 1, "Shop": 1}


def test_parse_enrichment_combines_all_three():
    response = {
        "orders": {"edges": [{"node": {"tags": ["family"]}}, {"node": {"tags": []}}]},
        "codeDiscountNodes": {"edges": [{"node": {"codeDiscount": {
            "codes": {"edges": [{"node": {"code": "WELCOME10"}}]}, "asyncUsageCount": 2}}}]},
        "publications": {"edges": [{"node": {"name": "Online Store"}}]},
    }
    out = parse_enrichment(response)
    assert out["order_split"] == {"public": 1, "proof": 1}
    assert out["welcome10_uses"] == 2
    assert out["publication_counts"] == {"Online Store": 1}


def test_parse_enrichment_tolerates_garbage():
    assert parse_enrichment(None)["order_split"] == {"public": 0, "proof": 0}
    assert parse_enrichment({})["welcome10_uses"] == 0


def test_enrichment_feeds_the_section_end_to_end():
    """The parser output is exactly the shape build_auralis_today_section consumes."""
    from src.brief.auralis_today import build_auralis_today_section

    enrichment = parse_enrichment({
        "orders": {"edges": [{"node": {"tags": []}}, {"node": {"tags": ["family"]}}]},
        "codeDiscountNodes": {"edges": [{"node": {"codeDiscount": {
            "codes": {"edges": [{"node": {"code": "WELCOME10"}}]}, "asyncUsageCount": 1}}}]},
        "publications": {"edges": [{"node": {"name": "Online Store"}}]},
    })
    shopify = {"orders": {"order_count": 2}, "products": {"active_products": 33}, **enrichment}
    section = build_auralis_today_section({
        "shopify": shopify,
        "owner_actions": [{"content": "Meta verification", "ownership": "needs_chris",
                           "gates_revenue": True, "smallest_step": "click Verify"}],
        "promotion_queue": ["hooded sherpas"],
    })
    revenue = next(i for i in section.items if i.startswith("Revenue:"))
    assert "1 public sale" in revenue and "WELCOME10 x1" in revenue
