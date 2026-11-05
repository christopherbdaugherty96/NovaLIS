from __future__ import annotations

import re
from typing import Any

_VAGUE_DETAIL_RE = re.compile(
    r"^tell me more(?:\s+about\s+(?:that|it|this))?[.!?]*$",
    re.IGNORECASE,
)
_SOURCE_RE = re.compile(
    r"^what (?:are (?:the )?(?:(?:other|additional) )?sources (?:reporting|saying)|"
    r"do (?:the )?(?:(?:other|additional) )?sources say)"
    r"(?:\s+about\s+(?:that|it|this))?[.!?]*$",
    re.IGNORECASE,
)
_AGREEMENT_RE = re.compile(
    r"^(?:do (?:those|the|these) sources agree|do they agree|"
    r"are (?:those|the|these) sources in agreement|"
    r"is there agreement (?:among|between) (?:those|the|these) sources)[.!?]*$",
    re.IGNORECASE,
)
_SIGNIFICANCE_RE = re.compile(
    r"^(?:explain )?why (?:does )?(?:this|that|it) matter(?:s)?[.!?]*$",
    re.IGNORECASE,
)
_TOPIC_STOPWORDS = {
    "about",
    "again",
    "can",
    "could",
    "current",
    "details",
    "does",
    "explain",
    "happening",
    "information",
    "into",
    "more",
    "news",
    "now",
    "please",
    "report",
    "reporting",
    "say",
    "saying",
    "show",
    "situation",
    "sources",
    "tell",
    "that",
    "the",
    "their",
    "them",
    "these",
    "they",
    "this",
    "those",
    "today",
    "what",
    "why",
    "with",
    "would",
}


def _clean_text(value: Any, *, limit: int) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit]


def _search_results(payload: Any) -> list[dict[str, str]]:
    if not isinstance(payload, dict):
        return []
    widget = payload.get("widget")
    if not isinstance(widget, dict) or widget.get("type") != "search":
        return []
    data = widget.get("data")
    raw_results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(raw_results, list):
        return []

    results: list[dict[str, str]] = []
    for raw in raw_results[:10]:
        if not isinstance(raw, dict):
            continue
        result = {
            "title": _clean_text(raw.get("title"), limit=300),
            "source": _clean_text(raw.get("source") or raw.get("domain"), limit=160),
            "url": _clean_text(raw.get("url") or raw.get("link"), limit=1000),
            "description": _clean_text(
                raw.get("description") or raw.get("snippet") or raw.get("summary"),
                limit=1000,
            ),
        }
        if any(result.values()):
            results.append(result)
    return results


def record_news_evidence_result(
    session_state: dict[str, Any],
    *,
    query: str,
    success: bool,
    payload: Any,
) -> None:
    """Replace the active search-evidence state with this exact governed result."""
    results = _search_results(payload) if success else []
    session_state["active_news_evidence"] = {
        "query": _clean_text(query, limit=500),
        "status": "available" if results else "unavailable",
        "results": results,
    }
    if not results:
        # A new failed/empty retrieval must not inherit evidence from an older topic.
        session_state["last_sources"] = []
        session_state["last_source_links"] = []
        session_state.pop("search_widget", None)


def _followup_kind(query: str) -> str:
    normalized = _clean_text(query, limit=500)
    if _VAGUE_DETAIL_RE.fullmatch(normalized):
        return "detail"
    if _SOURCE_RE.fullmatch(normalized):
        return "sources"
    if _AGREEMENT_RE.fullmatch(normalized):
        return "agreement"
    if _SIGNIFICANCE_RE.fullmatch(normalized):
        return "significance"
    return ""


def _format_retrieved_results(results: list[dict[str, str]]) -> str:
    lines = ["Here is the reporting I actually retrieved:"]
    for result in results[:5]:
        source = result.get("source") or "Retrieved source"
        title = result.get("title") or "Untitled result"
        description = result.get("description")
        line = f"- {source}: {title}"
        if description:
            line += f" — {description}"
        lines.append(line)
    return "\n".join(lines)


def answer_news_evidence_followup(query: str, session_state: dict[str, Any]) -> str | None:
    """Answer evidence-dependent follow-ups without allowing unsupported current claims."""
    kind = _followup_kind(query)
    if not kind:
        return None
    evidence = session_state.get("active_news_evidence")
    if not isinstance(evidence, dict) or not evidence.get("query"):
        return None

    results = evidence.get("results")
    available_results = results if isinstance(results, list) else []
    if evidence.get("status") != "available" or not available_results:
        if kind == "detail":
            return "I can't add verified current details because that retrieval did not succeed."
        if kind == "sources":
            return "No additional sources were retrieved, so I can't report what other sources are saying."
        if kind == "agreement":
            return "I can't say whether sources agree because no current source evidence was retrieved."
        return (
            "I can offer general background, but I couldn't verify the current development or why it "
            "matters today from retrieved sources."
        )

    if kind in {"detail", "sources"}:
        return _format_retrieved_results(available_results)
    if kind == "agreement":
        return (
            "I retrieved the source information above, but I have not established a supported "
            "cross-source agreement comparison."
        )
    return (
        "The retrieved material can support the factual details shown above, but it does not by itself "
        "establish a verified explanation of why the development matters."
    )


def _topic_terms(value: Any) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", str(value or "").lower())
        if len(token) >= 4 and token not in _TOPIC_STOPWORDS
    }


def _explicit_topic_terms(query: str) -> set[str]:
    normalized = _clean_text(query, limit=500).strip(".?! ")
    patterns = (
        r"\b(?:about|regarding|concerning)\s+(.+)$",
        r"^(?:explain|describe|discuss)\s+(.+)$",
        r"^what (?:is|are)\s+(.+)$",
        r"^how (?:does|do)\s+(.+?)\s+work$",
    )
    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if not match:
            continue
        subject = match.group(1).strip()
        if subject.lower() in {"that", "this", "it", "them", "those", "these"}:
            return set()
        return _topic_terms(subject)
    return set()


def retire_news_evidence_for_unrelated_turn(
    query: str,
    session_state: dict[str, Any],
) -> None:
    """Retire follow-up eligibility when GeneralChat takes over an explicit new topic."""
    evidence = session_state.get("active_news_evidence")
    if not isinstance(evidence, dict):
        return
    active_terms = _topic_terms(evidence.get("query"))
    incoming_terms = _explicit_topic_terms(query)
    if active_terms and incoming_terms and active_terms.isdisjoint(incoming_terms):
        session_state["active_news_evidence"] = {}
