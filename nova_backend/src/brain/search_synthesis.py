"""Deterministic search evidence synthesis for Cap 16.

This module turns governed search results into structured evidence metadata.
It does not search, browse, call LLMs, route capabilities, or authorize action.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class EvidenceClaim:
    claim: str
    source_url: str
    source_title: str = ""
    confidence: EvidenceConfidence = EvidenceConfidence.MEDIUM
    uncertainty: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "claim": self.claim,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "confidence": self.confidence.value,
            "uncertainty": self.uncertainty,
        }


@dataclass(frozen=True)
class SearchEvidence:
    query: str
    claims: list[EvidenceClaim] = field(default_factory=list)
    known: list[str] = field(default_factory=list)
    unclear: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    confidence: EvidenceConfidence = EvidenceConfidence.LOW
    evidence_status: str = "no_evidence"
    source_pages_read: int = 0
    result_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "claims": [claim.to_dict() for claim in self.claims],
            "known": list(self.known),
            "unclear": list(self.unclear),
            "source_urls": list(self.source_urls),
            "confidence": self.confidence.value,
            "evidence_status": self.evidence_status,
            "source_pages_read": self.source_pages_read,
            "result_count": self.result_count,
        }


_QUERY_STOPWORDS = {
    "about",
    "after",
    "again",
    "against",
    "answer",
    "around",
    "before",
    "brief",
    "current",
    "does",
    "find",
    "from",
    "give",
    "headline",
    "headlines",
    "latest",
    "look",
    "news",
    "nonexistent",
    "report",
    "result",
    "results",
    "search",
    "show",
    "source",
    "sources",
    "summary",
    "tell",
    "this",
    "topic",
    "topics",
    "what",
    "when",
    "where",
    "with",
}


def synthesize_search_evidence(
    *,
    query: str,
    results: list[dict],
    source_packets: list[dict] | None = None,
    low_relevance: bool = False,
) -> SearchEvidence:
    """Build a deterministic evidence packet from governed search outputs."""
    normalized_query = " ".join(str(query or "").split()).strip()
    clean_results = [item for item in list(results or []) if isinstance(item, dict)]
    clean_packets = [item for item in list(source_packets or []) if isinstance(item, dict)]
    source_urls = _unique_urls(clean_results, clean_packets)

    weak_query_match = _weak_query_match(normalized_query, clean_results, clean_packets)
    if low_relevance or not clean_results:
        return SearchEvidence(
            query=normalized_query,
            claims=[],
            known=[],
            unclear=[
                "Search returned little reliable evidence for the requested claim or entity.",
                "The query may be misspelled, fictional, private, too new, or not covered by reliable indexed sources.",
            ],
            source_urls=source_urls,
            confidence=EvidenceConfidence.LOW,
            evidence_status="weak_or_no_evidence",
            source_pages_read=len(clean_packets),
            result_count=len(clean_results),
        )

    claims = _claims_from_packets(clean_packets)
    if not claims:
        claims = _claims_from_results(clean_results)
    if weak_query_match:
        claims = _downgrade_claims_for_weak_match(claims)

    known: list[str] = []
    if clean_results:
        known.append(
            f"Governed search returned {len(clean_results)} result{'s' if len(clean_results) != 1 else ''}."
        )
    if clean_packets:
        known.append(
            f"Nova reviewed {len(clean_packets)} source page{'s' if len(clean_packets) != 1 else ''}."
        )
    if source_urls:
        known.append("Visible source URLs are available for review.")

    unclear: list[str] = []
    if not clean_packets:
        unclear.append("Source pages were not readable, so evidence is based on result titles/snippets.")
    elif len(clean_packets) < min(3, len(clean_results)):
        unclear.append("Only part of the result set had readable source-page text.")
    if weak_query_match:
        unclear.append("Results may be weak or unrelated because visible result text barely matches the query.")
    unclear.append("Current facts may change; use the linked sources for latest context.")

    confidence = _confidence_for(clean_results, clean_packets, claims, weak_query_match=weak_query_match)
    status = "source_backed" if clean_packets else "snippet_backed"
    return SearchEvidence(
        query=normalized_query,
        claims=claims,
        known=known,
        unclear=unclear,
        source_urls=source_urls,
        confidence=confidence,
        evidence_status=status,
        source_pages_read=len(clean_packets),
        result_count=len(clean_results),
    )


def render_evidence_notes(evidence: SearchEvidence) -> tuple[str, str, str]:
    """Return user-facing confidence/known/unclear lines from evidence."""
    confidence = evidence.confidence.value.replace("_", " ").title()
    known = " ".join(evidence.known).strip() or "No strong evidence was found."
    unclear = " ".join(evidence.unclear).strip() or "No major uncertainty was detected from available evidence."
    return confidence, known, unclear


def _claims_from_packets(source_packets: list[dict]) -> list[EvidenceClaim]:
    claims: list[EvidenceClaim] = []
    for packet in source_packets[:3]:
        url = str(packet.get("url") or "").strip()
        if not url:
            continue
        title = _clean_text(str(packet.get("title") or ""))
        text = _clean_text(str(packet.get("text") or ""))
        claim_text = _first_sentence(text) or title
        if not claim_text:
            continue
        claims.append(
            EvidenceClaim(
                claim=claim_text,
                source_url=url,
                source_title=title,
                confidence=EvidenceConfidence.MEDIUM,
                uncertainty="Source-page excerpt was available; details may still need verification.",
            )
        )
    return claims


def _claims_from_results(results: list[dict]) -> list[EvidenceClaim]:
    claims: list[EvidenceClaim] = []
    for item in results[:3]:
        url = str(item.get("url") or "").strip()
        if not url:
            continue
        title = _clean_text(str(item.get("title") or ""))
        snippet = _clean_text(str(item.get("snippet") or ""))
        claim_text = snippet or title
        if not claim_text:
            continue
        claims.append(
            EvidenceClaim(
                claim=claim_text,
                source_url=url,
                source_title=title,
                confidence=EvidenceConfidence.LOW,
                uncertainty="Only search result title/snippet was available.",
            )
        )
    return claims


def _downgrade_claims_for_weak_match(claims: list[EvidenceClaim]) -> list[EvidenceClaim]:
    downgraded: list[EvidenceClaim] = []
    for claim in claims:
        uncertainty = str(claim.uncertainty or "").strip()
        relevance_note = "Visible result text barely matches the query; this claim may be weak or unrelated."
        if relevance_note not in uncertainty:
            uncertainty = f"{uncertainty} {relevance_note}".strip()
        downgraded.append(
            EvidenceClaim(
                claim=claim.claim,
                source_url=claim.source_url,
                source_title=claim.source_title,
                confidence=EvidenceConfidence.LOW,
                uncertainty=uncertainty,
            )
        )
    return downgraded


def _confidence_for(
    results: list[dict],
    source_packets: list[dict],
    claims: list[EvidenceClaim],
    *,
    weak_query_match: bool = False,
) -> EvidenceConfidence:
    if weak_query_match:
        return EvidenceConfidence.LOW
    if len(source_packets) >= 2 and len(claims) >= 2:
        return EvidenceConfidence.HIGH
    if source_packets or results:
        return EvidenceConfidence.MEDIUM
    return EvidenceConfidence.LOW


def _unique_urls(results: list[dict], source_packets: list[dict]) -> list[str]:
    urls: list[str] = []
    for collection in (source_packets, results):
        for item in collection:
            url = str(item.get("url") or "").strip()
            if url and url not in urls:
                urls.append(url)
    return urls


def _clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", str(value or ""))
    return " ".join(text.split()).strip()


def _meaningful_tokens(value: str) -> set[str]:
    tokens = set()
    for token in re.findall(r"[a-z0-9]{3,}", str(value or "").lower()):
        if token.isdigit() or token in _QUERY_STOPWORDS:
            continue
        tokens.add(token)
    return tokens


def _weak_query_match(query: str, results: list[dict], source_packets: list[dict]) -> bool:
    query_tokens = _meaningful_tokens(query)
    if not query_tokens:
        return False

    visible_parts: list[str] = []
    for item in list(results or []) + list(source_packets or []):
        if not isinstance(item, dict):
            continue
        for key in ("title", "snippet", "text", "url"):
            visible_parts.append(str(item.get(key) or ""))
    visible_tokens = _meaningful_tokens(" ".join(visible_parts))
    if not visible_tokens:
        return True

    overlap = query_tokens & visible_tokens
    return len(overlap) / max(1, len(query_tokens)) < 0.25


def _first_sentence(text: str) -> str:
    clean = _clean_text(text)
    if not clean:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", clean, maxsplit=1)
    sentence = parts[0].strip()
    if len(sentence) > 260:
        sentence = sentence[:257].rstrip() + "..."
    return sentence
