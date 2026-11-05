from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

_EMPTY_ACTIVITY_PREFIX = "I do not have correlated action evidence"


def _clean(value: Any, *, limit: int = 220) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _available_user_topics(session_context: Iterable[Mapping[str, Any]]) -> list[str]:
    topics: list[str] = []
    for item in session_context:
        if not isinstance(item, Mapping) or str(item.get("role") or "").lower() != "user":
            continue
        content = _clean(item.get("content"))
        if content and content not in topics:
            topics.append(content)
    return topics[-8:]


def _news_evidence_lines(active_news_evidence: Any) -> list[str]:
    if not isinstance(active_news_evidence, Mapping):
        return []
    query = _clean(active_news_evidence.get("query"))
    if not query:
        return []
    results = active_news_evidence.get("results")
    available_results = results if isinstance(results, list) else []
    if active_news_evidence.get("status") != "available" or not available_results:
        return [
            f'- Retrieval failed for "{query}"; no current sources were retrieved.',
            "- Current developments and source agreement remain unverified.",
        ]

    source_labels: list[str] = []
    for raw in available_results[:5]:
        if not isinstance(raw, Mapping):
            continue
        source = _clean(raw.get("source"), limit=100)
        title = _clean(raw.get("title"), limit=160)
        label = ": ".join(part for part in (source, title) if part)
        if label:
            source_labels.append(label)
    lines = [f'- Governed retrieval for "{query}" returned {len(available_results)} result(s).']
    lines.extend(f"  - Retrieved evidence: {label}" for label in source_labels)
    lines.append("- Retrieval records what Nova obtained; it does not independently prove each source claim.")
    return lines


def _verified_activity_lines(activity_recap: str) -> list[str]:
    lines: list[str] = []
    for raw in str(activity_recap or "").splitlines():
        cleaned = _clean(raw.lstrip("- "), limit=500)
        if not cleaned or cleaned.startswith("What I can verify from current-session evidence"):
            continue
        if cleaned.startswith("Evidence boundary:"):
            break
        if raw.lstrip().startswith("-"):
            lines.append(cleaned)
        elif lines:
            lines[-1] = _clean(f"{lines[-1]} {cleaned}", limit=500)
    return lines


def render_local_conversation_summary(
    *,
    session_context: Iterable[Mapping[str, Any]],
    active_news_evidence: Any = None,
    activity_recap: str = "",
) -> str:
    """Render an evidence-labeled recap without model inference or external access."""
    topics = _available_user_topics(session_context)
    evidence_lines = _news_evidence_lines(active_news_evidence)
    verified_activity = str(activity_recap or "").strip()
    has_verified_activity = bool(
        verified_activity and not verified_activity.startswith(_EMPTY_ACTIVITY_PREFIX)
    )
    if not topics and not evidence_lines and not has_verified_activity:
        return (
            "I do not have enough prior conversation in the history currently available to summarize. "
            "No external search was performed."
        )

    lines = ["Summary of the conversation history currently available to me:"]
    if topics:
        lines.append("What you asked or discussed:")
        lines.extend(f'- "{topic}"' for topic in topics)
    if evidence_lines:
        lines.append("News evidence status:")
        lines.extend(evidence_lines)
    if has_verified_activity:
        lines.append("Verified session activity:")
        lines.extend(f"- {line}" for line in _verified_activity_lines(verified_activity))
    lines.extend(
        [
            "Evidence boundary: assistant-generated conversation text is not independently verified "
            "and was not promoted into factual evidence by this summary.",
            "This summary covers only the bounded history still available in this session.",
        ]
    )
    return "\n".join(lines)
