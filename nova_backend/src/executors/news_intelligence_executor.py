from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

from src.actions.action_result import ActionResult
from src.llm.llm_gateway import generate_chat
from src.rendering.intelligence_brief_renderer import IntelligenceBriefRenderer
from src.utils.content_extractor import extract_text_from_html

MAX_HEADLINES_PER_SUMMARY = 3
LLM_TIMEOUT_SECONDS = 8.0
SOURCE_READ_TIMEOUT_SECONDS = 8.0
MAX_SOURCE_PAGES_PER_BRIEF = 4
MAX_SOURCE_TEXT_CHARS = 3500
MAX_CLUSTER_STORIES = 4
MAX_RELATED_PAIRS = 3
MAX_HEADLINE_SUMMARY_CHARS = 320

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

HEADLINE_STOPWORDS = STOPWORDS | {
    "video",
    "shows",
    "story",
    "today",
    "latest",
    "update",
    "updates",
    "still",
    "just",
    "more",
    "amid",
    "while",
}

HEADLINE_TERM_NORMALIZATION = {
    "iranian": "iran",
    "israeli": "israel",
    "american": "usa",
    "british": "uk",
    "chinese": "china",
    "russian": "russia",
    "ukrainian": "ukraine",
}


class NewsIntelligenceExecutor:
    """Governed analysis over user-selected news headlines (invocation-bound)."""
    def __init__(self, network: Any | None = None) -> None:
        self.renderer = IntelligenceBriefRenderer()
        self.network = network

    @staticmethod
    def _speakable_preview(text: str, *, limit: int = 220) -> str:
        clean = re.sub(r"\s+", " ", str(text or "").strip())
        if len(clean) <= limit:
            return clean
        return clean[: limit - 3].rstrip() + "..."

    def _ok_result(
        self,
        message: str,
        *,
        data: dict[str, Any] | None = None,
        request_id: str | None = None,
        speakable_text: str | None = None,
    ) -> ActionResult:
        payload = dict(data or {})
        return ActionResult.ok(
            message=message,
            data=payload,
            structured_data=payload,
            speakable_text=speakable_text or self._speakable_preview(message),
            request_id=request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def _failure_result(
        self,
        message: str,
        *,
        request_id: str | None = None,
        failure_kind: str,
        data: dict[str, Any] | None = None,
    ) -> ActionResult:
        payload = dict(data or {})
        payload.setdefault("failure_kind", failure_kind)
        return ActionResult.failure(
            message=message,
            data=payload,
            structured_data=payload,
            speakable_text=message,
            request_id=request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
            outcome_reason=message,
        )

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
                    "published": (item.get("published") or "").strip(),
                    "video_url": (item.get("video_url") or "").strip(),
                }
            )
        return out

    def _sanitize_categories(self, raw: Any) -> dict[str, dict[str, Any]]:
        if not isinstance(raw, dict):
            return {}
        out: dict[str, dict[str, Any]] = {}
        for key, bucket in raw.items():
            normalized_key = str(key or "").strip().lower()
            if not normalized_key or not isinstance(bucket, dict):
                continue
            items = self._sanitize_headlines(bucket.get("items"))
            if not items:
                continue
            out[normalized_key] = {
                "title": str(bucket.get("title") or normalized_key.title()).strip() or normalized_key.title(),
                "summary": str(bucket.get("summary") or "").strip(),
                "items": items,
            }
        return out

    def _load_developing_stories(self) -> list[dict[str, Any]]:
        root = Path(__file__).resolve().parents[3] / "nova_workspace" / "story_tracker"
        tracked_path = root / "tracked_topics.json"
        try:
            tracked = json.loads(tracked_path.read_text(encoding="utf-8"))
            topics = tracked.get("topics", []) if isinstance(tracked, dict) else []
        except Exception:
            topics = []

        out: list[dict[str, Any]] = []
        for topic in topics:
            t = str(topic).strip()
            if not t:
                continue
            slug = re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_") or "untitled"
            story_path = root / f"story_{slug}.json"
            try:
                story = json.loads(story_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            snapshots = story.get("snapshots", []) if isinstance(story, dict) else []
            out.append({"topic": t, "updates": len(snapshots)})
        return out

    def _apply_story_evolution(self, headlines: list[dict[str, str]], developing_stories: list[dict[str, Any]]) -> list[dict[str, Any]]:
        enhanced: list[dict[str, Any]] = []
        for item in headlines:
            cloned = dict(item)
            title_text = (item.get("title") or "").lower()
            for story in developing_stories:
                topic = str(story.get("topic") or "")
                updates = int(story.get("updates") or 0)
                topic_terms = [term for term in re.findall(r"[a-zA-Z0-9]+", topic.lower()) if len(term) >= 4]
                if topic_terms and any(term in title_text for term in topic_terms):
                    cloned["evolution_cycles"] = updates
                    break
            enhanced.append(cloned)
        return enhanced

    def _select_headlines(self, headlines: list[dict[str, str]], params: dict[str, Any]) -> tuple[list[dict[str, str]], list[int]]:
        selection = (params or {}).get("selection")
        if selection == "all":
            selected = headlines[:MAX_HEADLINES_PER_SUMMARY]
            indices = list(range(1, len(selected) + 1))
            return selected, indices

        if selection == "source":
            source_query = str((params or {}).get("source_query") or "").strip().lower()
            if source_query:
                selected: list[dict[str, str]] = []
                indices: list[int] = []
                for i, item in enumerate(headlines, start=1):
                    source = str(item.get("source") or "").strip().lower()
                    if source and (source_query in source or source in source_query):
                        selected.append(item)
                        indices.append(i)
                    if len(selected) >= MAX_HEADLINES_PER_SUMMARY:
                        break
                return selected, indices

        if selection == "topic":
            topic_query = str((params or {}).get("topic_query") or "").strip().lower()
            if topic_query:
                topic_terms = [term for term in re.findall(r"[a-zA-Z0-9]+", topic_query) if len(term) >= 3]
                selected: list[dict[str, str]] = []
                indices: list[int] = []
                for i, item in enumerate(headlines, start=1):
                    merged = f"{item.get('title', '')} {item.get('summary', '')}".lower()
                    if topic_terms and all(term in merged for term in topic_terms):
                        selected.append(item)
                        indices.append(i)
                    elif topic_query in merged:
                        selected.append(item)
                        indices.append(i)
                    if len(selected) >= MAX_HEADLINES_PER_SUMMARY:
                        break
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

    def _select_category_headlines(
        self,
        categories: dict[str, dict[str, Any]],
        category_key: str,
    ) -> tuple[list[dict[str, str]], list[int], str]:
        normalized = str(category_key or "").strip().lower()
        if not normalized:
            return [], [], ""
        bucket = categories.get(normalized)
        if not isinstance(bucket, dict):
            return [], [], ""
        items = self._sanitize_headlines(bucket.get("items"))
        selected = items[:MAX_HEADLINES_PER_SUMMARY]
        indices = list(range(1, len(selected) + 1))
        title = str(bucket.get("title") or normalized.title()).strip() or normalized.title()
        return selected, indices, title

    def _headline_prompt(self, item: dict[str, str], index: int, article_excerpt: str = "") -> str:
        summary = str(item.get("summary") or "").strip()
        excerpt_block = ""
        if article_excerpt:
            excerpt_block = f"\nArticle excerpt (source-page read):\n{article_excerpt[:1800]}\n"
        elif summary:
            excerpt_block = f"\nFeed synopsis:\n{summary}\n"
        return (
            "Summarize this news headline in 2-3 factual sentences.\n"
            "Do not use section headers, bullets, or speculation.\n"
            "If detail is limited, explicitly note that it is headline-level only.\n"
            "If an article excerpt is provided, prioritize excerpt facts over headline text.\n\n"
            f"Headline #{index}: {item['title']}\n"
            f"Source: {item.get('source', 'Unknown')}\n"
            f"URL: {item.get('url', 'N/A')}\n"
            f"{excerpt_block}"
            "Return plain text only."
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

    def _llm_or_fallback(
        self,
        prompt: str,
        fallback: str,
        request_id: str,
        *,
        session_id: str | None = None,
        timeout_seconds: float | None = None,
        max_tokens: int = 550,
    ) -> str:
        effective_timeout = LLM_TIMEOUT_SECONDS if timeout_seconds is None else timeout_seconds
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(
            generate_chat,
            prompt,
            mode="analysis_only",
            safety_profile="analysis",
            request_id=request_id,
            session_id=session_id,
            max_tokens=max_tokens,
            temperature=0.2,
        )
        try:
            text = future.result(timeout=effective_timeout)
            return text or fallback
        except FuturesTimeoutError:
            future.cancel()
            return fallback
        except Exception:
            return fallback
        finally:
            # wait=True ensures timed-out work cannot continue after return.
            pool.shutdown(wait=True, cancel_futures=True)

    def _fetch_source_text(
        self,
        url: str,
        capability_id: int,
        *,
        request_id: str | None = None,
        session_id: str | None = None,
    ) -> str:
        cleaned_url = (url or "").strip()
        if not cleaned_url or self.network is None:
            return ""
        try:
            response = self.network.request(
                capability_id=capability_id,
                method="GET",
                url=cleaned_url,
                as_json=False,
                timeout=6,
                request_id=request_id,
                session_id=session_id,
            )
            html = str(response.get("text") or "")
            if not html:
                return ""
            return extract_text_from_html(html, max_chars=MAX_SOURCE_TEXT_CHARS).strip()
        except Exception:
            return ""

    def _collect_source_packets(
        self,
        headlines: list[dict[str, str]],
        capability_id: int,
        *,
        request_id: str | None = None,
        session_id: str | None = None,
    ) -> list[dict[str, str]]:
        packets: list[dict[str, str]] = []
        seen_urls: set[str] = set()
        for item in headlines:
            url = (item.get("url") or "").strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            text = self._fetch_source_text(
                url,
                capability_id=capability_id,
                request_id=request_id,
                session_id=session_id,
            )
            if not text:
                continue
            packets.append(
                {
                    "title": (item.get("title") or "").strip(),
                    "source": (item.get("source") or "").strip() or "Unknown",
                    "url": url,
                    "text": text,
                }
            )
            if len(packets) >= MAX_SOURCE_PAGES_PER_BRIEF:
                break
        return packets

    def _source_brief_prompt(self, packets: list[dict[str, str]]) -> str:
        blocks: list[str] = []
        for idx, packet in enumerate(packets, start=1):
            blocks.append(
                f"[{idx}] {packet['title']}\n"
                f"Source: {packet['source']}\n"
                f"URL: {packet['url']}\n"
                f"Excerpt: {packet['text'][:1800]}"
            )
        joined = "\n\n".join(blocks)
        return (
            "You are preparing a merged summary of today's news using provided source-page excerpts only.\n"
            "Do not invent facts not present in excerpts.\n"
            "Use exactly these sections:\n"
            "Executive Summary\nWhat Happened\nCross-Source Signals\nSource Coverage\n\n"
            "Include source names inline when making key claims.\n\n"
            f"{joined}"
        )

    def _source_brief_fallback(self, packets: list[dict[str, str]]) -> str:
        lines = [
            "Executive Summary",
            "[Fallback] Source-grounded synthesis is unavailable right now.",
            "",
            "What Happened",
            "- I could not safely merge source-page evidence for this request.",
            "",
            "Cross-Source Signals",
            "- Not enough verified source excerpts were available.",
            "",
            "Source Coverage",
        ]
        for idx, packet in enumerate(packets[:6], start=1):
            lines.append(f"- [{idx}] {packet['source']} - {packet['url']}")
        if not packets:
            lines.append("- No source pages were available in this run.")
        return "\n".join(lines)

    def _cluster_label(self, title: str, text: str) -> str:
        merged = f"{title} {text}".lower()
        if any(k in merged for k in ("war", "conflict", "ceasefire", "strike", "military", "gaza", "ukraine", "iran", "israel")):
            return "Global Security"
        if any(k in merged for k in ("inflation", "economy", "federal reserve", "rates", "jobs", "market", "gdp")):
            return "Economy & Markets"
        if any(k in merged for k in ("ai", "technology", "chip", "semiconductor", "model", "software")):
            return "Technology"
        if any(k in merged for k in ("election", "congress", "senate", "policy", "regulation", "law")):
            return "Policy & Government"
        return "General Developments"

    def _cluster_packets(self, packets: list[dict[str, str]]) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for packet in packets:
            label = self._cluster_label(packet.get("title", ""), packet.get("text", ""))
            grouped[label].append(packet)

        clusters: list[dict[str, Any]] = []
        for label, items in grouped.items():
            if not items:
                continue
            cluster_sources = []
            for item in items:
                src = (item.get("source") or "Unknown").strip()
                if src not in cluster_sources:
                    cluster_sources.append(src)
            clusters.append(
                {
                    "title": label,
                    "items": items[:MAX_CLUSTER_STORIES],
                    "sources": cluster_sources[:6],
                }
            )
        clusters.sort(key=lambda c: len(c.get("items", [])), reverse=True)
        return clusters[:4]

    def _cluster_prompt(self, cluster: dict[str, Any]) -> str:
        items = cluster.get("items", [])
        blocks = []
        for item in items:
            blocks.append(
                f"Title: {item.get('title','')}\n"
                f"Source: {item.get('source','Unknown')}\n"
                f"URL: {item.get('url','')}\n"
                f"Excerpt: {str(item.get('text',''))[:1200]}"
            )
        joined = "\n\n".join(blocks)
        return (
            f"Topic: {cluster.get('title','General Developments')}\n"
            "Write a concise neutral synthesis using these sections exactly:\n"
            "Summary\nImplication\n\n"
            "Use only provided excerpts.\n\n"
            f"{joined}"
        )

    def _cluster_fallback(self, cluster: dict[str, Any]) -> tuple[str, str]:
        items = cluster.get("items", [])
        if not items:
            return (
                "[Fallback] I couldn't derive a verified summary from source excerpts.",
                "Check back after more source details are available.",
            )
        top_title = str(items[0].get("title") or "Top development").strip()
        return (
            f"[Fallback] {top_title}. I could not complete a source-grounded synthesis for this topic.",
            "Treat this as a placeholder and review the linked source pages directly.",
        )

    def _parse_summary_and_implication(
        self,
        text: str,
        cluster: dict[str, Any],
        *,
        use_fallback: bool = True,
    ) -> tuple[str, str]:
        raw = str(text or "").strip()
        if not raw:
            if use_fallback:
                return self._cluster_fallback(cluster)
            return "", ""

        summary_match = re.search(r"Summary\s*(.+?)(?:\n\s*Implication|\Z)", raw, flags=re.IGNORECASE | re.DOTALL)
        implication_match = re.search(r"Implication\s*(.+)$", raw, flags=re.IGNORECASE | re.DOTALL)

        summary = (summary_match.group(1).strip() if summary_match else "").strip(" -:\n")
        implication = (implication_match.group(1).strip() if implication_match else "").strip(" -:\n")

        if not summary or not implication:
            if not use_fallback:
                return "", ""
            fb_summary, fb_implication = self._cluster_fallback(cluster)
            summary = summary or fb_summary
            implication = implication or fb_implication
        return summary, implication

    def _render_daily_brief_v2(self, clusters: list[dict[str, Any]]) -> tuple[str, list[str]]:
        lines = [
            "NOVA DAILY INTELLIGENCE BRIEF",
            "Major Themes Today",
            "------------------",
        ]
        all_sources: list[str] = []
        for idx, cluster in enumerate(clusters, start=1):
            summary = str(cluster.get("summary") or "").strip()
            implication = str(cluster.get("implication") or "").strip()
            sources = [s for s in (cluster.get("sources") or []) if str(s).strip()]
            for src in sources:
                if src not in all_sources:
                    all_sources.append(src)

            lines.extend(
                [
                    "",
                    f"Story {idx}: {cluster.get('title', 'General Developments')}",
                    f"Summary: {summary}",
                    f"Implication: {implication}",
                    f"Sources: {', '.join(sources) if sources else 'Unknown'}",
                ]
            )

        coverage = []
        for cluster in clusters:
            title = str(cluster.get("title") or "").strip()
            if title and title not in coverage:
                coverage.append(title)

        lines.extend(
            [
                "",
                f"Confidence: {'Medium-High' if len(all_sources) >= 4 else 'Medium'}",
                f"Sources used: {len(all_sources)}",
                f"Coverage: {', '.join(coverage) if coverage else 'General'}",
            ]
        )
        return "\n".join(lines), all_sources

    def _expand_cluster(self, clusters: list[dict[str, Any]], story_id: int) -> ActionResult:
        idx = int(story_id) - 1
        if idx < 0 or idx >= len(clusters):
            return self._failure_result(
                "I couldn't find that story number in the latest brief.",
                failure_kind="brief_story_not_found",
                data={"story_id": story_id},
            )
        cluster = clusters[idx]
        title = str(cluster.get("title") or "General Developments")
        summary = str(cluster.get("summary") or "")
        implication = str(cluster.get("implication") or "")
        items = cluster.get("items") or []
        sources = cluster.get("sources") or []
        lines = [
            f"Story {story_id}: {title}",
            "",
            f"Summary: {summary}",
            f"Implication: {implication}",
            "",
            "Supporting headlines:",
        ]
        for item in items[:4]:
            lines.append(f"- {item.get('title','Unknown')} ({item.get('source','Unknown')})")
        lines.append("")
        lines.append(f"Sources: {', '.join(sources) if sources else 'Unknown'}")
        return self._ok_result(
            "\n".join(lines),
            data={"sources": sources, "story_id": story_id},
            speakable_text=f"Story {story_id}. {self._speakable_preview(summary or implication, limit=170)}",
        )

    def _compare_clusters(self, clusters: list[dict[str, Any]], left_story_id: int, right_story_id: int) -> ActionResult:
        left_idx = int(left_story_id) - 1
        right_idx = int(right_story_id) - 1
        if left_idx < 0 or right_idx < 0 or left_idx >= len(clusters) or right_idx >= len(clusters):
            return self._failure_result(
                "I couldn't compare those story numbers from the latest brief.",
                failure_kind="brief_compare_not_found",
                data={"left_story_id": left_story_id, "right_story_id": right_story_id},
            )
        left = clusters[left_idx]
        right = clusters[right_idx]
        lines = [
            f"Comparison: Story {left_story_id} vs Story {right_story_id}",
            "",
            f"Story {left_story_id} ({left.get('title','')}): {left.get('summary','')}",
            f"Story {right_story_id} ({right.get('title','')}): {right.get('summary','')}",
            "",
            "Implication contrast:",
            f"- Story {left_story_id}: {left.get('implication','')}",
            f"- Story {right_story_id}: {right.get('implication','')}",
            "",
            f"Sources: {', '.join((left.get('sources') or []) + (right.get('sources') or []))}",
        ]
        merged_sources = []
        for src in (left.get("sources") or []) + (right.get("sources") or []):
            if src not in merged_sources:
                merged_sources.append(src)
        comparison_text = (
            f"{str(left.get('title') or '').strip()} compared with "
            f"{str(right.get('title') or '').strip()}"
        ).strip()
        return self._ok_result(
            "\n".join(lines),
            data={"sources": merged_sources[:10], "comparison": {"left_story_id": left_story_id, "right_story_id": right_story_id}},
            speakable_text=(
                f"Compared story {left_story_id} and story {right_story_id}. "
                f"{self._speakable_preview(comparison_text, limit=140)}"
            ),
        )

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

    def _headline_summary_fallback(self, item: dict[str, str]) -> str:
        title = str(item.get("title") or "").strip()
        source = str(item.get("source") or "").strip() or "Unknown source"
        published = self._format_published_value(str(item.get("published") or "").strip())
        if not title:
            return "Limited detail is available from the headline alone."
        details_note = "Limited detail is available from the headline alone. Confirm in the full source report."
        if published:
            details_note = f"{details_note} Published: {published}."
        return f"{source} reports: {title}. {details_note}"

    def _normalize_headline_summary(self, text: str, item: dict[str, str]) -> str:
        raw = str(text or "").strip()
        if not raw:
            return self._headline_summary_fallback(item)

        cleaned_lines: list[str] = []
        for line in raw.splitlines():
            candidate = str(line or "").strip()
            if not candidate:
                continue
            if re.fullmatch(
                r"(summary|key points?|context|implications?|signal|watch|headline|detailed story analysis|reference)",
                candidate,
                flags=re.IGNORECASE,
            ):
                continue
            candidate = re.sub(r"^\s*[-*]\s*", "", candidate)
            candidate = re.sub(r"^\s*headline\s*#?\d+\s*:\s*", "", candidate, flags=re.IGNORECASE)
            cleaned_lines.append(candidate)

        if not cleaned_lines:
            return self._headline_summary_fallback(item)

        merged = " ".join(cleaned_lines)
        merged = re.sub(r"\s+", " ", merged).strip()
        if not merged:
            return self._headline_summary_fallback(item)
        merged = self._dedupe_sentences(merged)
        if len(merged) > MAX_HEADLINE_SUMMARY_CHARS:
            merged = merged[: MAX_HEADLINE_SUMMARY_CHARS - 3].rstrip() + "..."
        if len(merged) < 24:
            return self._headline_summary_fallback(item)
        return merged

    def _dedupe_sentences(self, text: str) -> str:
        raw_sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]
        if not raw_sentences:
            return text.strip()
        deduped: list[str] = []
        seen_keys: set[str] = set()
        for sentence in raw_sentences:
            key = re.sub(r"[^a-z0-9]+", " ", sentence.lower()).strip()
            if not key or key in seen_keys:
                continue
            seen_keys.add(key)
            deduped.append(sentence)
            if len(deduped) >= 3:
                break
        merged = " ".join(deduped).strip()
        if merged and merged[-1] not in ".!?":
            merged += "."
        return merged or text.strip()

    def _format_published_value(self, published: str) -> str:
        value = str(published or "").strip()
        if not value:
            return ""
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                parsed = datetime.strptime(value, fmt)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            except ValueError:
                continue
        return value

    def _headline_terms(self, item: dict[str, str]) -> set[str]:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        terms: set[str] = set()
        for token in re.findall(r"[a-zA-Z]{4,}", text):
            normalized = HEADLINE_TERM_NORMALIZATION.get(token, token)
            if normalized in HEADLINE_STOPWORDS:
                continue
            terms.add(normalized)
        return terms

    def _related_headline_pairs(self, headlines: list[dict[str, str]]) -> list[dict[str, Any]]:
        scored_pairs: list[dict[str, Any]] = []
        indexed = list(enumerate(headlines, start=1))
        for (left_idx, left_item), (right_idx, right_item) in combinations(indexed, 2):
            shared = sorted(self._headline_terms(left_item) & self._headline_terms(right_item))
            if not shared:
                continue
            score = len(shared)
            if score <= 0:
                continue
            scored_pairs.append(
                {
                    "left_index": left_idx,
                    "right_index": right_idx,
                    "shared_terms": shared[:6],
                    "score": score,
                }
            )

        scored_pairs.sort(key=lambda item: item["score"], reverse=True)
        return scored_pairs[:MAX_RELATED_PAIRS]

    def _render_related_comparison_section(self, headlines: list[dict[str, str]], pairs: list[dict[str, Any]]) -> str:
        if not pairs:
            return ""

        lines = [
            "",
            "RELATED STORY COMPARISON",
            "------------------------",
        ]
        for pair in pairs:
            left_idx = int(pair.get("left_index") or 0)
            right_idx = int(pair.get("right_index") or 0)
            if left_idx <= 0 or right_idx <= 0 or left_idx > len(headlines) or right_idx > len(headlines):
                continue
            shared_terms = [str(term) for term in (pair.get("shared_terms") or []) if str(term).strip()]
            shared_text = ", ".join(shared_terms[:4]) if shared_terms else "overlapping topic language"
            left_title = str(headlines[left_idx - 1].get("title") or "").strip()
            right_title = str(headlines[right_idx - 1].get("title") or "").strip()
            lines.extend(
                [
                    f"- Story {left_idx} and Story {right_idx} overlap on: {shared_text}.",
                    f"  Story {left_idx}: {left_title}",
                    f"  Story {right_idx}: {right_title}",
                    f"  Compare command: compare headlines {left_idx} and {right_idx}",
                ]
            )
        return "\n".join(lines)

    def _render_headline_report(
        self,
        selected: list[dict[str, str]],
        summaries: list[str],
        *,
        selected_indices: list[int] | None = None,
        report_title: str = "HEADLINE-BY-HEADLINE SUMMARY",
    ) -> tuple[str, list[dict[str, Any]]]:
        lines = [
            report_title,
            "----------------------------",
        ]
        for offset, (item, summary) in enumerate(zip(selected, summaries), start=1):
            display_index = (
                selected_indices[offset - 1]
                if isinstance(selected_indices, list) and (offset - 1) < len(selected_indices)
                else offset
            )
            title = str(item.get("title") or "Unknown headline").strip()
            source = str(item.get("source") or "Unknown").strip()
            url = str(item.get("url") or "").strip()
            lines.extend(
                [
                    "",
                    f"Story {display_index}",
                    f"Source: {source}",
                    f"Headline: {title}",
                    f"Summary: {summary}",
                ]
            )
            published = self._format_published_value(str(item.get("published") or "").strip())
            if published:
                lines.append(f"Published: {published}")
            if url:
                lines.append(f"Reference: {url}")
            video_url = str(item.get("video_url") or "").strip()
            if video_url:
                lines.append(f"Video: {video_url}")

        related_pairs = self._related_headline_pairs(selected)
        related_text = self._render_related_comparison_section(selected, related_pairs)
        if related_text:
            lines.append(related_text)
        return "\n".join(lines), related_pairs

    def _compare_headline_indices(
        self,
        headlines: list[dict[str, str]],
        left_index: int,
        right_index: int,
        *,
        request_id: str | None = None,
    ) -> ActionResult:
        if left_index == right_index:
            return self._failure_result(
                "Choose two different headline numbers to compare.",
                request_id=request_id,
                failure_kind="duplicate_headline_compare",
                data={"left_index": left_index, "right_index": right_index},
            )
        if left_index < 1 or right_index < 1 or left_index > len(headlines) or right_index > len(headlines):
            return self._failure_result(
                "I couldn't compare those headline numbers from the current list.",
                request_id=request_id,
                failure_kind="headline_compare_not_found",
                data={"left_index": left_index, "right_index": right_index},
            )

        left = headlines[left_index - 1]
        right = headlines[right_index - 1]
        shared = sorted(self._headline_terms(left) & self._headline_terms(right))
        shared_terms = ", ".join(shared[:8]) if shared else "No strong overlap terms were detected."

        lines = [
            f"HEADLINE COMPARISON - Story {left_index} vs Story {right_index}",
            "",
            f"Story {left_index}: {left.get('title', 'Unknown')}",
            f"Source: {left.get('source', 'Unknown')}",
            "",
            f"Story {right_index}: {right.get('title', 'Unknown')}",
            f"Source: {right.get('source', 'Unknown')}",
            "",
            f"Shared terms: {shared_terms}",
        ]
        if shared:
            lines.append("These stories appear related and should be reviewed together for context alignment.")
        else:
            lines.append("These stories appear distinct based on headline-level text.")
        payload = {
            "widget": {
                "type": "news_summary",
                "data": {
                    "comparison": {"left": left_index, "right": right_index, "shared_terms": shared[:8]},
                    "summary_text": "\n".join(lines).strip(),
                },
            },
            "related_pairs": [{"left_index": left_index, "right_index": right_index, "shared_terms": shared[:8]}],
        }
        return self._ok_result(
            "\n".join(lines),
            data=payload,
            request_id=request_id,
            speakable_text=(
                f"Headline comparison ready for story {left_index} and story {right_index}. "
                f"Shared terms: {self._speakable_preview(shared_terms, limit=120)}"
            ),
        )

    def _story_page_prompt(self, item: dict[str, str], story_index: int, source_text: str) -> str:
        return (
            "Summarize the source-page article for this story using only the provided excerpt.\n"
            "Use exactly these sections:\n"
            "Article Summary\nKey Facts\nWhy It Matters\n\n"
            "Keep the summary factual and concise. Do not speculate.\n\n"
            f"Story #{story_index}: {str(item.get('title') or '').strip()}\n"
            f"Source: {str(item.get('source') or 'Unknown').strip()}\n"
            f"URL: {str(item.get('url') or '').strip()}\n\n"
            f"Excerpt:\n{source_text[:2600]}"
        )

    def _story_page_fallback_from_text(self, source_text: str) -> str:
        normalized = re.sub(r"\s+", " ", str(source_text or "").strip())
        if not normalized:
            return (
                "Article Summary\n"
                "I could not extract enough readable article text.\n\n"
                "Key Facts\n"
                "- Source page text extraction returned limited detail.\n\n"
                "Why It Matters\n"
                "Use the source link directly and try this request again."
            )

        sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", normalized) if segment.strip()]
        summary_sentences = sentences[:3] if sentences else [normalized[:260]]
        summary = " ".join(summary_sentences).strip()
        if len(summary) > 420:
            summary = summary[:417].rstrip() + "..."
        return (
            "Article Summary\n"
            f"{summary}\n\n"
            "Key Facts\n"
            "- This fallback was generated directly from source-page text extraction.\n"
            "- Ask again to regenerate with a richer model response.\n\n"
            "Why It Matters\n"
            "This reflects source-page content, not headline-only interpretation."
        )

    def _normalize_story_page_summary(self, text: str, fallback: str) -> str:
        raw = str(text or "").strip()
        if not raw:
            return fallback
        cleaned = re.sub(r"\r\n?", "\n", raw).strip()
        if len(cleaned) > 1600:
            cleaned = cleaned[:1597].rstrip() + "..."
        if "Article Summary" not in cleaned:
            cleaned = f"Article Summary\n{cleaned}"
        if "Key Facts" not in cleaned:
            cleaned = f"{cleaned}\n\nKey Facts\n- Additional source details are available in the reference link."
        if "Why It Matters" not in cleaned:
            cleaned = (
                f"{cleaned}\n\nWhy It Matters\n"
                "This summary is based on source-page article text gathered at request time."
            )
        return cleaned

    def _summarize_story_page(self, request, headlines: list[dict[str, str]], story_index: int, session_id: str | None) -> ActionResult:
        if story_index < 1 or story_index > len(headlines):
            return self._failure_result(
                "I couldn't find that story number in the current headlines.",
                request_id=request.request_id,
                failure_kind="story_page_not_found",
                data={"story_index": story_index},
            )

        item = headlines[story_index - 1]
        url = str(item.get("url") or "").strip()
        if not url:
            return self._failure_result(
                f"Story {story_index} does not have a source URL to read.",
                request_id=request.request_id,
                failure_kind="story_page_missing_url",
                data={"story_index": story_index},
            )

        source_text = self._fetch_source_text(
            url,
            capability_id=request.capability_id,
            request_id=f"{request.request_id}:story-page:{story_index}",
            session_id=session_id,
        )
        if not source_text:
            return self._failure_result(
                (
                    f"I couldn't read the article page for story {story_index} right now. "
                    "Try again, or open the source link and ask once the page is accessible."
                ),
                request_id=request.request_id,
                failure_kind="story_page_unavailable",
                data={"story_index": story_index, "url": url},
            )

        fallback = self._story_page_fallback_from_text(source_text)
        analysis = self._llm_or_fallback(
            self._story_page_prompt(item, story_index, source_text),
            fallback,
            request_id=f"{request.request_id}:story-page-analysis:{story_index}",
            session_id=session_id,
            timeout_seconds=SOURCE_READ_TIMEOUT_SECONDS,
            max_tokens=520,
        )
        normalized = self._normalize_story_page_summary(analysis, fallback)

        lines = [
            f"STORY PAGE SUMMARY - Story {story_index}",
            "",
            f"Source: {str(item.get('source') or 'Unknown').strip()}",
            f"Headline: {str(item.get('title') or 'Unknown headline').strip()}",
        ]
        published = self._format_published_value(str(item.get("published") or "").strip())
        if published:
            lines.append(f"Published: {published}")
        lines.extend(
            [
                "",
                normalized,
                "",
                f"Reference: {url}",
            ]
        )

        payload = {
            "widget": {
                "type": "news_summary",
                "data": {
                    "selection": "story_page",
                    "story_index": story_index,
                    "source_read": True,
                    "headline": str(item.get("title") or "").strip(),
                    "source": str(item.get("source") or "").strip(),
                    "url": url,
                    "summary_text": normalized,
                },
            },
            "story_index": story_index,
        }
        return self._ok_result(
            "\n".join(lines).strip(),
            data=payload,
            request_id=request.request_id,
            speakable_text=f"Story page summary ready for story {story_index}. {self._speakable_preview(normalized, limit=170)}",
        )

    def execute_summary(self, request) -> ActionResult:
        headlines = self._sanitize_headlines((request.params or {}).get("headlines"))
        categories = self._sanitize_categories((request.params or {}).get("categories"))
        session_id = str((request.params or {}).get("session_id") or "").strip() or None
        if not headlines:
            return self._failure_result(
                "I don't have current headlines cached yet. Ask for today's news to refresh headlines, then I can summarize them.",
                request_id=request.request_id,
                failure_kind="missing_headline_cache",
            )

        action = str((request.params or {}).get("action") or "").strip().lower()
        if action == "story_page_summary":
            try:
                story_index = int((request.params or {}).get("story_index") or 0)
            except Exception:
                story_index = 0
            return self._summarize_story_page(
                request,
                headlines,
                story_index,
                session_id,
            )

        if action == "compare_indices":
            try:
                left_index = int((request.params or {}).get("left_index") or 0)
                right_index = int((request.params or {}).get("right_index") or 0)
            except Exception:
                left_index = 0
                right_index = 0
            return self._compare_headline_indices(
                headlines,
                left_index,
                right_index,
                request_id=request.request_id,
            )

        selection = str((request.params or {}).get("selection") or "").strip().lower()
        report_title = "HEADLINE-BY-HEADLINE SUMMARY"
        selected: list[dict[str, str]]
        indices: list[int]

        if selection == "category":
            requested_category = str((request.params or {}).get("category_key") or "").strip().lower()
            selected, indices, category_title = self._select_category_headlines(categories, requested_category)
            if category_title:
                report_title = f"CATEGORY SUMMARY - {category_title}"
        else:
            selected, indices = self._select_headlines(headlines, request.params or {})

        if not selected:
            if selection == "source":
                wanted_source = str((request.params or {}).get("source_query") or "").strip()
                available_sources = sorted(
                    {
                        str(item.get("source") or "").strip()
                        for item in headlines
                        if str(item.get("source") or "").strip()
                    }
                )
                source_list = ", ".join(available_sources[:8]) or "no sources available"
                return self._failure_result(
                    f"I couldn't find recent headlines for {wanted_source}. Available sources: {source_list}.",
                    request_id=request.request_id,
                    failure_kind="source_not_found",
                    data={"selection": selection, "source_query": wanted_source},
                )
            if selection == "topic":
                wanted_topic = str((request.params or {}).get("topic_query") or "").strip()
                return self._failure_result(
                    f"I couldn't find recent headlines for topic '{wanted_topic}'. Try a broader term.",
                    request_id=request.request_id,
                    failure_kind="topic_not_found",
                    data={"selection": selection, "topic_query": wanted_topic},
                )
            if selection == "category":
                requested_category = str((request.params or {}).get("category_key") or "").strip().lower()
                available_categories = ", ".join(sorted(categories.keys())) if categories else "none"
                return self._failure_result(
                    f"I couldn't find category '{requested_category}'. Available categories: {available_categories}.",
                    request_id=request.request_id,
                    failure_kind="category_not_found",
                    data={"selection": selection, "category_key": requested_category},
                )
            return self._failure_result(
                "I couldn't match those headline numbers. Try: summarize headline 1.",
                request_id=request.request_id,
                failure_kind="headline_selection_not_found",
                data={"selection": selection or "indices"},
            )

        if len(selected) > MAX_HEADLINES_PER_SUMMARY:
            return self._failure_result(
                "Please select up to three headlines per request.",
                request_id=request.request_id,
                failure_kind="headline_selection_limit",
                data={"selection_count": len(selected)},
            )

        normalized_summaries: list[str] = []
        for item, idx in zip(selected, indices):
            fallback = self._headline_summary_fallback(item)
            article_excerpt = self._fetch_source_text(
                str(item.get("url") or ""),
                capability_id=request.capability_id,
                request_id=f"{request.request_id}:article:{idx}",
                session_id=session_id,
            )
            analysis = self._llm_or_fallback(
                self._headline_prompt(item, idx, article_excerpt=article_excerpt),
                fallback,
                request_id=f"{request.request_id}:headline:{idx}",
                session_id=session_id,
            )
            normalized_summaries.append(self._normalize_headline_summary(analysis, item))

        report, related_pairs = self._render_headline_report(
            selected,
            normalized_summaries,
            selected_indices=indices,
            report_title=report_title,
        )

        payload = {
            "widget": {
                "type": "news_summary",
                "data": {
                    "indices": indices,
                    "count": len(selected),
                    "selection": selection or "indices",
                    "category_key": (request.params or {}).get("category_key"),
                    "summary_text": report,
                },
            },
            "related_pairs": related_pairs,
        }
        return self._ok_result(
            report,
            data=payload,
            request_id=request.request_id,
            speakable_text=(
                f"Headline summary ready for {len(selected)} stor"
                f"{'ies' if len(selected) != 1 else 'y'}. "
                f"{self._speakable_preview(report, limit=170)}"
            ),
        )

    def execute_brief(self, request) -> ActionResult:
        session_id = str((request.params or {}).get("session_id") or "").strip() or None
        action = str((request.params or {}).get("action") or "").strip().lower()
        brief_clusters = (request.params or {}).get("brief_clusters")
        cluster_state = brief_clusters if isinstance(brief_clusters, list) else []
        if action == "expand_cluster":
            story_id = int((request.params or {}).get("story_id") or 0)
            return self._expand_cluster(cluster_state, story_id)
        if action == "compare_clusters":
            left_story_id = int((request.params or {}).get("left_story_id") or 0)
            right_story_id = int((request.params or {}).get("right_story_id") or 0)
            return self._compare_clusters(cluster_state, left_story_id, right_story_id)
        if action == "track_cluster":
            story_id = int((request.params or {}).get("story_id") or 0)
            idx = story_id - 1
            if idx < 0 or idx >= len(cluster_state):
                return self._failure_result(
                    "I couldn't find that story number in the latest brief.",
                    request_id=request.request_id,
                    failure_kind="brief_story_not_found",
                    data={"story_id": story_id},
                )
            topic = str(cluster_state[idx].get("title") or "").strip()
            return self._ok_result(
                f"Track request ready for story {story_id}: {topic}",
                data={"track_topic": topic, "story_id": story_id},
                request_id=request.request_id,
                speakable_text=f"Track request ready for story {story_id}: {topic}",
            )

        headlines = self._sanitize_headlines((request.params or {}).get("headlines"))
        if not headlines:
            return self._failure_result(
                "I couldn't build a daily brief because I don't have current headlines yet. Ask for today's news to refresh headlines, then try again.",
                request_id=request.request_id,
                failure_kind="missing_headline_cache",
            )

        source = headlines[:6]
        read_sources = bool((request.params or {}).get("read_sources"))
        degraded_note = ""
        if read_sources:
            packets = self._collect_source_packets(
                source,
                capability_id=request.capability_id,
                request_id=request.request_id,
                session_id=session_id,
            )
            if packets:
                clusters = self._cluster_packets(packets)
                rendered_clusters: list[dict[str, Any]] = []
                omitted_clusters = 0
                placeholder_clusters = 0
                for cluster in clusters:
                    analysis = self._llm_or_fallback(
                        self._cluster_prompt(cluster),
                        "",
                        request_id=f"{request.request_id}:cluster:{cluster.get('title','general')}",
                        session_id=session_id,
                        timeout_seconds=SOURCE_READ_TIMEOUT_SECONDS,
                        max_tokens=380,
                    )
                    fallback_summary, fallback_implication = self._cluster_fallback(cluster)
                    summary, implication = self._parse_summary_and_implication(
                        analysis,
                        cluster,
                        use_fallback=True,
                    )
                    if not summary or not implication:
                        omitted_clusters += 1
                        continue
                    if summary == fallback_summary or implication == fallback_implication:
                        placeholder_clusters += 1
                    rendered_clusters.append(
                        {
                            "id": len(rendered_clusters) + 1,
                            "title": cluster.get("title", "General Developments"),
                            "summary": summary,
                            "implication": implication,
                            "sources": cluster.get("sources", []),
                            "items": cluster.get("items", []),
                        }
                    )

                if not rendered_clusters:
                    degraded_note = (
                        "Note: I couldn't finish the full source-grounded brief in time, "
                        "so this is a quicker headline-only brief. You can retry with today's news or narrow the topic."
                    )
                else:
                    report, all_sources = self._render_daily_brief_v2(rendered_clusters)
                    if placeholder_clusters:
                        report = (
                            f"{report}\n\nNote: {placeholder_clusters} topic cluster(s) are using placeholder source-grounded summaries because synthesis was unavailable."
                        )
                    if omitted_clusters:
                        report = (
                            f"{report}\n\nNote: {omitted_clusters} topic cluster(s) were omitted due to incomplete source-grounded synthesis."
                        )
                    payload = {
                        "widget": {
                            "type": "intelligence_brief",
                            "data": {
                                "headline_count": len(source),
                                "source_pages_read": len(packets),
                                "cluster_count": len(rendered_clusters),
                                "placeholder_cluster_count": placeholder_clusters,
                                "omitted_cluster_count": omitted_clusters,
                            },
                        },
                        "brief_clusters": rendered_clusters,
                        "sources": all_sources,
                    }
                    return self._ok_result(
                        report.strip(),
                        data=payload,
                        request_id=request.request_id,
                        speakable_text=(
                            "Daily intelligence brief ready. "
                            f"{len(rendered_clusters)} topic clusters across {len(all_sources)} sources."
                        ),
                    )
            else:
                degraded_note = (
                    "Note: I couldn't read enough source pages in time, "
                    "so this is a quicker headline-only brief. You can retry with today's news or narrow the topic."
                )

        developing_stories = self._load_developing_stories()
        source = self._apply_story_evolution(source, developing_stories)
        fallback_headlines = "\n".join(f"{idx}. {item['title']}" for idx, item in enumerate(source[:4], start=1))
        fallback = (
            "Top Headlines\n"
            f"{fallback_headlines}\n\n"
            "Key Developments\n- Multiple notable stories are active right now.\n\n"
            "Signals to Watch\n- Monitor follow-up reporting from primary sources."
        )
        analysis = self._llm_or_fallback(
            self._brief_prompt(source),
            fallback,
            request_id=f"{request.request_id}:brief",
            session_id=session_id,
        )
        brief = self.renderer.render_brief(
            source,
            analysis_text=analysis,
            developing_stories=developing_stories,
        )
        if degraded_note:
            brief = f"{degraded_note}\n\n{brief}"

        prior = (request.params or {}).get("topic_history")
        prior_map = prior if isinstance(prior, dict) else {}
        topic_map = self._build_topic_map(source, prior_map)

        payload = {
            "widget": {"type": "intelligence_brief", "data": {"headline_count": len(source)}},
            "topic_map": topic_map,
        }
        return self._ok_result(
            brief.strip(),
            data=payload,
            request_id=request.request_id,
            speakable_text=(
                f"{'Headline-only brief ready. ' if degraded_note else 'Daily intelligence brief ready. '}"
                f"{self._speakable_preview(brief, limit=170)}"
            ),
        )

    def execute_topic_map(self, request) -> ActionResult:
        headlines = self._sanitize_headlines((request.params or {}).get("headlines"))
        prior = (request.params or {}).get("topic_history")
        prior_map = prior if isinstance(prior, dict) else {}
        topic_map = self._build_topic_map(headlines, prior_map)

        if not topic_map:
            return self._failure_result(
                "No topic map is available yet. Ask for news first.",
                request_id=request.request_id,
                failure_kind="topic_map_unavailable",
            )

        lines = ["TOPIC MEMORY MAP"]
        for idx, (topic, weight) in enumerate(topic_map.items(), start=1):
            lines.append(f"{idx}. {topic} ({weight})")

        payload = {"widget": {"type": "topic_map", "data": {"topics": topic_map}}, "topic_map": topic_map}
        return self._ok_result(
            "\n".join(lines),
            data=payload,
            request_id=request.request_id,
            speakable_text=f"Topic memory map ready with {len(topic_map)} topic{'s' if len(topic_map) != 1 else ''}.",
        )
