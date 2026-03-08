from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.actions.action_result import ActionResult
from src.llm.llm_gateway import generate_chat
from src.rendering.intelligence_brief_renderer import IntelligenceBriefRenderer
from src.utils.content_extractor import extract_text_from_html

MAX_HEADLINES_PER_SUMMARY = 3
LLM_TIMEOUT_SECONDS = 8.0
SOURCE_READ_TIMEOUT_SECONDS = 8.0
MAX_SOURCE_PAGES_PER_BRIEF = 6
MAX_SOURCE_TEXT_CHARS = 3500
MAX_CLUSTER_STORIES = 4

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
    def __init__(self, network: Any | None = None) -> None:
        self.renderer = IntelligenceBriefRenderer()
        self.network = network

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
            "Today's major developments were merged from source-page reads across top outlets.",
            "",
            "What Happened",
        ]
        for idx, packet in enumerate(packets[:5], start=1):
            lines.append(f"- [{idx}] {packet['title']} ({packet['source']})")
        lines.extend(
            [
                "",
                "Cross-Source Signals",
                "- Multiple sources report overlapping developments from different angles.",
                "",
                "Source Coverage",
            ]
        )
        for idx, packet in enumerate(packets[:6], start=1):
            lines.append(f"- [{idx}] {packet['source']} - {packet['url']}")
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
            return ("No reliable detail available from the current sources.", "Monitor primary-source updates.")
        top_title = str(items[0].get("title") or "Top development")
        return (
            f"{top_title}. Related outlets describe similar developments within this topic.",
            "This development may affect near-term planning and risk posture.",
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
            return ActionResult.failure("I couldn't find that story number in the latest brief.")
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
        return ActionResult.ok(message="\n".join(lines), data={"sources": sources})

    def _compare_clusters(self, clusters: list[dict[str, Any]], left_story_id: int, right_story_id: int) -> ActionResult:
        left_idx = int(left_story_id) - 1
        right_idx = int(right_story_id) - 1
        if left_idx < 0 or right_idx < 0 or left_idx >= len(clusters) or right_idx >= len(clusters):
            return ActionResult.failure("I couldn't compare those story numbers from the latest brief.")
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
        return ActionResult.ok(message="\n".join(lines), data={"sources": merged_sources[:10]})

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
        session_id = str((request.params or {}).get("session_id") or "").strip() or None
        if not headlines:
            return ActionResult.failure(
                "No cached headlines found. Say 'news' first, then choose headline numbers.",
                request_id=request.request_id,
            )

        selected, indices = self._select_headlines(headlines, request.params or {})
        if not selected:
            selection = str((request.params or {}).get("selection") or "")
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
                return ActionResult.failure(
                    f"I couldn't find recent headlines for {wanted_source}. Available sources: {source_list}.",
                    request_id=request.request_id,
                )
            if selection == "topic":
                wanted_topic = str((request.params or {}).get("topic_query") or "").strip()
                return ActionResult.failure(
                    f"I couldn't find recent headlines for topic '{wanted_topic}'. Try a broader term.",
                    request_id=request.request_id,
                )
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
                session_id=session_id,
            )
            blocks.append(self.renderer.render_single(item, analysis_text=analysis.strip()))

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
                return ActionResult.failure("I couldn't find that story number in the latest brief.")
            topic = str(cluster_state[idx].get("title") or "").strip()
            return ActionResult.ok(message=f"Track request ready for story {story_id}: {topic}", data={"track_topic": topic})

        headlines = self._sanitize_headlines((request.params or {}).get("headlines"))
        if not headlines:
            return ActionResult.failure(
                "No cached headlines found. Say 'news' first, then ask for a daily brief.",
                request_id=request.request_id,
            )

        source = headlines[:6]
        read_sources = bool((request.params or {}).get("read_sources"))
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
                synthesis_failures = 0
                for cluster in clusters:
                    analysis = self._llm_or_fallback(
                        self._cluster_prompt(cluster),
                        "",
                        request_id=f"{request.request_id}:cluster:{cluster.get('title','general')}",
                        session_id=session_id,
                        timeout_seconds=SOURCE_READ_TIMEOUT_SECONDS,
                        max_tokens=380,
                    )
                    summary, implication = self._parse_summary_and_implication(
                        analysis,
                        cluster,
                        use_fallback=False,
                    )
                    if not summary or not implication:
                        synthesis_failures += 1
                        continue
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
                    return ActionResult.failure(
                        "I couldn't generate a source-grounded brief right now. Please try again in a moment.",
                        request_id=request.request_id,
                    )

                report, all_sources = self._render_daily_brief_v2(rendered_clusters)
                if synthesis_failures:
                    report = (
                        f"{report}\n\nNote: {synthesis_failures} topic cluster(s) were omitted due to incomplete source-grounded synthesis."
                    )
                return ActionResult.ok(
                    message=report.strip(),
                    data={
                        "widget": {
                            "type": "intelligence_brief",
                            "data": {
                                "headline_count": len(source),
                                "source_pages_read": len(packets),
                                "cluster_count": len(rendered_clusters),
                            },
                        },
                        "brief_clusters": rendered_clusters,
                        "sources": all_sources,
                    },
                    request_id=request.request_id,
                    authority_class="read_only",
                    external_effect=False,
                    reversible=True,
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

        prior = (request.params or {}).get("topic_history")
        prior_map = prior if isinstance(prior, dict) else {}
        topic_map = self._build_topic_map(source, prior_map)

        return ActionResult.ok(
            message=brief.strip(),
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
