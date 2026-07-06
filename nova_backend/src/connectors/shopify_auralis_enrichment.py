"""Auralis Today (C1) — read-only Shopify enrichment parsers.

Turns Shopify GraphQL response fragments into the three C1 enrichment fields:
order public/proof split, WELCOME10 usage, and per-channel publication counts.

These are PURE PARSERS, unit-tested against mock fragments. The GraphQL query below is
documented but its live round-trip is gated on Cap 65 P5 (live-store sign-off), which is
owner-paused — so this module does not add a network call to the on-open path. When P5 is
unpaused, a thin connector method runs AURALIS_ENRICHMENT_QUERY and passes the response to
parse_enrichment(); until then, Auralis Today degrades honestly (base order counts, no split).

Read-only. No writes. No new capability authority.
"""

from __future__ import annotations

from typing import Any

# Order tags that mark a non-public (custom/family/proof) order. Public = orders with none.
DEFAULT_PROOF_TAGS = frozenset({"family", "custom", "proof", "wholesale"})

# Documented for the P5-gated fetch. Field shapes match the Shopify Admin GraphQL API;
# validate against a dev store before wiring a live call (per connector P5 requirement).
AURALIS_ENRICHMENT_QUERY = """
query AuralisEnrichment($orderQuery: String!) {
  orders(first: 250, query: $orderQuery) {
    edges { node { tags } }
    pageInfo { hasNextPage }
  }
  codeDiscountNodes(first: 100) {
    edges { node { codeDiscount { __typename
      ... on DiscountCodeBasic { codes(first: 1) { edges { node { code } } } asyncUsageCount }
    } } }
  }
  publications(first: 25) {
    edges { node { name } }
  }
}
"""


def parse_order_split(order_edges: Any, proof_tags: frozenset[str] = DEFAULT_PROOF_TAGS) -> dict[str, int]:
    """Split orders into public vs family/proof by tag. Missing tags -> public."""
    public = 0
    proof = 0
    for edge in order_edges or []:
        tags = ((edge or {}).get("node") or {}).get("tags") or []
        norm = {str(t).strip().lower() for t in tags if str(t).strip()}
        if norm & proof_tags:
            proof += 1
        else:
            public += 1
    return {"public": public, "proof": proof}


def parse_welcome10_uses(discount_edges: Any, code: str = "WELCOME10") -> int:
    """Total usage count for a named discount code across matching discount nodes."""
    target = code.strip().upper()
    total = 0
    for edge in discount_edges or []:
        node = ((edge or {}).get("node") or {}).get("codeDiscount") or {}
        codes = ((node.get("codes") or {}).get("edges")) or []
        names = {
            str(((c or {}).get("node") or {}).get("code") or "").strip().upper()
            for c in codes
        }
        if target in names:
            try:
                total += int(node.get("asyncUsageCount") or 0)
            except (TypeError, ValueError):
                pass
    return total


def parse_publication_counts(publication_edges: Any) -> dict[str, int]:
    """Map each sales-channel publication name to a presence marker (1 = channel exists).

    Per-product publish counts require an additional per-publication read; v1 records channel
    presence, which is what the Status line needs ("N channels live").
    """
    counts: dict[str, int] = {}
    for edge in publication_edges or []:
        name = str(((edge or {}).get("node") or {}).get("name") or "").strip()
        if name:
            counts[name] = 1
    return counts


def parse_enrichment(response: Any, *, proof_tags: frozenset[str] = DEFAULT_PROOF_TAGS) -> dict[str, Any]:
    """Combine a full AURALIS_ENRICHMENT_QUERY response into the C1 enrichment dict."""
    data = response if isinstance(response, dict) else {}
    order_edges = ((data.get("orders") or {}).get("edges")) or []
    discount_edges = ((data.get("codeDiscountNodes") or {}).get("edges")) or []
    publication_edges = ((data.get("publications") or {}).get("edges")) or []
    return {
        "order_split": parse_order_split(order_edges, proof_tags),
        "welcome10_uses": parse_welcome10_uses(discount_edges),
        "publication_counts": parse_publication_counts(publication_edges),
    }
