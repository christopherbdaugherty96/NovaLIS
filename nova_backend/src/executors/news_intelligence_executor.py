from __future__ import annotations

import re
from collections import Counter
from typing import Any

from src.actions.action_result import ActionResult
from src.llm.llm_gateway import generate_chat

MAX_HEADLINES_PER_SUMMARY = 3

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "over",
    "under",
    "after",
    "before",
    "this",
    "that",
    "will",
    "would",
    "could",
    "should",
    "about",
    "their",
    "there",
    "have",
    "has",
    "had",
    "into",
    "new",
    "its",
}


class NewsIntelligenceExecutor:
    """Governed analysis over user-selected news headlines (invocation-bound)."""

    def _sanitize_headlines(self, raw: Any) -> list[dict[str, str]]:
        if not isinstance(raw, list):
            return []
        out: list[dict[str, str]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            title = (item.get("title") or "").strip()
            if not title:
                continue
            out.append(
                {
                    "title": title,
                    "source": (item.get("source") or "").strip(),
                    "url": (item.get("url") or "").strip(),
                    "summary": (item.get("summary") or "").strip(),
                }
            )
        return out

    def _select_headlines(self, headlines: list[dict[str, str]], params: dict[str, Any]) -> tuple[list[dict[str, str]], list[int]]:
        selection = (params or {}).get("selection")
        if selection == "all":
            selected = headlines[:MAX_HEADLINES_PER_SUMMARY]
            indices = list(range(1, len(selected) + 1))
            return selected, indices

        raw_indices = (params or {}).get("indices") or []
        indices: list[int] = []
        for value in raw_indices:
            try:
                idx = int(value)
            except Exception:
                continue
            if idx not in indices:
                indices.append(idx)

        selected: list[dict[str, str]] = []
        picked_indices: list[int] = []
        for idx in indices:
            if 1 <= idx <= len(headlines):
                selected.append(headlines[idx - 1])
                picked_indices.append(idx)
        return selected, picked_indices

    def _headline_prompt(self, item: dict[str, str], index: int) -> str:
        return (
            "Summarize this headline in a structured, factual format.\n"
            "Use exactly these sections:\n"
            "Summary\nKey Points\nContext\nImplications\n\n"
            f"Headline #{index}: {item['title']}\n"
            f"Source: {item.get('source', 'Unknown')}\n"
            f"URL: {item.get('url', 'N/A')}\n"
            "If details are uncertain from the headline alone, explicitly say that."
        )

    def _brief_prompt(self, headlines: list[dict[str, str]]) -> str:
        numbered = "\n".join(f"{idx}. {item['title']} ({item.get('source') or 'Unknown'})" for idx, item in enumerate(headlines, start=1))
        return (
            "Create a Daily Intelligence Brief from these headlines.\n"
            "Use exactly these sections:\n"
            "Top Headlines\nKey Developments\nSignals to Watch\n\n"
            "Keep it factual, compact, and non-predictive.\n\n"
            f"{numbered}"
        )

    def _llm_or_fallback(self, prompt: str, fallback: str, request_id: str) -> str:
        text = generate_chat(
            prompt,
            mode="analysis_only",
            safety_profile="analysis",
            request_id=request_id,
            max_tokens=550,
            temperature=0.2,
        )
        return text or fallback

    def _build_topic_map(self, headlines: list[dict[str, str]], prior: dict[str, int] | None = None) -> dict[str, int]:
        counts = Counter(prior or {})
        for item in headlines:
            words = re.findall(r"[a-zA-Z]{4,}", item.get("title", "").lower())
            for word in words:
                if word in STOPWORDS:
                    continue
                counts[word] += 1
        top = counts.most_common(12)
        return {topic: int(weight) for topic, weight in top}

    def execute_summary(self, request) -> ActionResult:
        headlines = self._sanitize_headlines((request.params or {}).get("headlines"))
        if not headlines:
            return ActionResult.failure(
                "No cached headlines found. Say 'news' first, then choose headline numbers.",
                request_id=request.request_id,
            )

        selected, indices = self._select_headlines(headlines, request.params or {})
        if not selected:
            return ActionResult.failure(
                "I couldn't match those headline numbers. Try: summarize headline 1.",
                request_id=request.request_id,
            )

        if len(selected) > MAX_HEADLINES_PER_SUMMARY:
            return ActionResult.failure(
                "Please select up to three headlines per request.",
                request_id=request.request_id,
            )

        blocks: list[str] = []
        for item, idx in zip(selected, indices):
            fallback = (
                f"Headline\n{item['title']}\n\n"
                "Summary\nLimited detail is available from the headline alone.\n\n"
                "Key Points\n- Review the source article for full facts.\n"
                f"- Source: {item.get('source') or 'Unknown'}\n\n"
                "Context\nThis summary is based on title-level information only.\n\n"
                "Implications\nPotential impact depends on details not present in the headline."
            )
            analysis = self._llm_or_fallback(
                self._headline_prompt(item, idx),
                fallback,
                request_id=f"{request.request_id}:headline:{idx}",
            )
            blocks.append(f"Headline {idx}: {item['title']}\n{analysis.strip()}")

        return ActionResult.ok(
            message="\n\n".join(blocks),
            data={
                "widget": {
                    "type": "news_summary",
                    "data": {"indices": indices, "count": len(selected)},
                }
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def execute_brief(self, request) -> ActionResult:
        headlines = self._sanitize_headlines((request.params or {}).get("headlines"))
        if not headlines:
            return ActionResult.failure(
                "No cached headlines found. Say 'news' first, then ask for a daily brief.",
                request_id=request.request_id,
            )

        source = headlines[:6]
        fallback_headlines = "\n".join(f"{idx}. {item['title']}" for idx, item in enumerate(source[:4], start=1))
        fallback = (
            "Top Headlines\n"
            f"{fallback_headlines}\n\n"
            "Key Developments\n- Multiple notable stories are active right now.\n\n"
            "Signals to Watch\n- Monitor follow-up reporting from primary sources."
        )
        brief = self._llm_or_fallback(
            self._brief_prompt(source),
            fallback,
            request_id=f"{request.request_id}:brief",
        )

        prior = (request.params or {}).get("topic_history")
        prior_map = prior if isinstance(prior, dict) else {}
        topic_map = self._build_topic_map(source, prior_map)

        return ActionResult.ok(
            message=f"DAILY INTELLIGENCE BRIEF\n\n{brief.strip()}",
            data={
                "widget": {"type": "intelligence_brief", "data": {"headline_count": len(source)}},
                "topic_map": topic_map,
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def execute_topic_map(self, request) -> ActionResult:
        headlines = self._sanitize_headlines((request.params or {}).get("headlines"))
        prior = (request.params or {}).get("topic_history")
        prior_map = prior if isinstance(prior, dict) else {}
        topic_map = self._build_topic_map(headlines, prior_map)

        if not topic_map:
            return ActionResult.failure(
                "No topic map is available yet. Ask for news first.",
                request_id=request.request_id,
            )

        lines = ["TOPIC MEMORY MAP"]
        for idx, (topic, weight) in enumerate(topic_map.items(), start=1):
            lines.append(f"{idx}. {topic} ({weight})")

        return ActionResult.ok(
            message="\n".join(lines),
            data={"widget": {"type": "topic_map", "data": {"topics": topic_map}}, "topic_map": topic_map},
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )
