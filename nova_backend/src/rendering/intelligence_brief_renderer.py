from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import re
from typing import Any


class IntelligenceBriefRenderer:
    """Deterministic formatting for invocation-bound intelligence briefing output."""

    @staticmethod
    def _bottom_line(text: str, *, fallback: str = "", limit: int = 220) -> str:
        clean = re.sub(r"\s+", " ", str(text or "").strip())
        if not clean:
            clean = re.sub(r"\s+", " ", str(fallback or "").strip())
        if not clean:
            clean = "No concise bottom line is available yet."
        if len(clean) <= limit:
            return clean
        return clean[: limit - 3].rstrip() + "..."

    @staticmethod
    def _derive_signal(text: str) -> str:
        lowered = (text or "").lower()
        if any(k in lowered for k in ("conflict", "tension", "sanction", "war")):
            return "Escalating institutional or geopolitical tension."
        if any(k in lowered for k in ("regulation", "policy", "law", "compliance")):
            return "Policy movement likely affecting governance or market structure."
        if any(k in lowered for k in ("ai", "chip", "technology", "semiconductor")):
            return "Technology sector development with potential medium-term impact."
        if any(k in lowered for k in ("economy", "inflation", "rates", "gdp")):
            return "Economic conditions may be shifting."
        return "Emerging development worth monitoring."

    @staticmethod
    def _derive_implication(text: str) -> str:
        lowered = (text or "").lower()
        if any(k in lowered for k in ("regulation", "policy", "law", "compliance")):
            return "Organizations in regulated sectors may face new compliance obligations."
        if any(k in lowered for k in ("chip", "semiconductor", "supply chain")):
            return "Technology supply and pricing dynamics may adjust across hardware markets."
        if any(k in lowered for k in ("conflict", "war", "sanction", "security")):
            return "Institutional risk posture may tighten as geopolitical uncertainty increases."
        if any(k in lowered for k in ("inflation", "rates", "economy")):
            return "Budget and investment planning may shift as macro signals evolve."
        return "This development may alter near-term operational planning."

    @staticmethod
    def _derive_watch(text: str) -> str:
        lowered = (text or "").lower()
        if any(k in lowered for k in ("senate", "congress", "parliament", "committee")):
            return "Watch upcoming committee or floor revisions."
        if any(k in lowered for k in ("earnings", "forecast", "guidance")):
            return "Watch next guidance cycle and official company disclosures."
        if any(k in lowered for k in ("conflict", "ceasefire", "military")):
            return "Watch official statements and verified follow-up reporting."
        return "Watch official follow-up reporting from primary sources."

    @staticmethod
    def _importance_confidence(text: str, source: str) -> tuple[str, str]:
        lowered = (text or "").lower()
        src = (source or "").lower()
        major_source = any(k in src for k in ("reuters", "ap", "associated press", "bbc", "npr", "wsj", "ft", "bloomberg"))
        high_driver = any(k in lowered for k in ("regulation", "policy", "sanction", "war", "security", "law"))
        medium_driver = any(k in lowered for k in ("ai", "technology", "chip", "semiconductor", "economy", "inflation"))

        if high_driver:
            importance = "HIGH"
        elif medium_driver:
            importance = "MEDIUM"
        else:
            importance = "LOW"

        confidence = "MEDIUM"
        if major_source:
            confidence = "HIGH" if importance in {"HIGH", "MEDIUM"} else "MEDIUM"
        return importance, confidence

    @staticmethod
    def _cluster_label(item: dict[str, Any]) -> str:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        if any(k in text for k in ("regulation", "policy", "law", "compliance")):
            return "AI REGULATION"
        if any(k in text for k in ("chip", "semiconductor", "gpu", "fabrication")):
            return "SEMICONDUCTORS"
        if any(k in text for k in ("war", "conflict", "sanction", "geopolit")):
            return "GEOPOLITICS"
        if any(k in text for k in ("economy", "inflation", "rates", "gdp")):
            return "ECONOMY"
        return "GENERAL DEVELOPMENTS"

    def _strategic_snapshot(self, headlines: list[dict[str, Any]]) -> str:
        if not headlines:
            return "No strategic movement detected from current inputs."
        labels: dict[str, int] = {}
        for item in headlines:
            label = self._cluster_label(item)
            labels[label] = labels.get(label, 0) + 1
        ranked = sorted(labels.items(), key=lambda kv: kv[1], reverse=True)[:2]
        focus = " and ".join(label.lower() for label, _ in ranked)
        return f"Key developments center on {focus}, with follow-up verification recommended."

    def _cross_story_insights(self, headlines: list[dict[str, Any]]) -> list[str]:
        token_counts: Counter[str] = Counter()
        for item in headlines[:8]:
            merged = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            for token in re.findall(r"[a-zA-Z]{4,}", merged):
                if token in {"this", "that", "with", "from", "into", "over", "under", "after", "before", "about"}:
                    continue
                token_counts[token] += 1

        shared_terms = [term for term, count in token_counts.items() if count >= 2]
        shared_terms = sorted(shared_terms, key=lambda t: token_counts[t], reverse=True)[:3]
        insights: list[str] = []

        for term in shared_terms:
            if term in {"regulation", "policy", "compliance", "governance", "senate", "congress"}:
                insights.append(
                    "Pattern: Regulatory pressure appears across multiple stories.\n"
                    "Why it matters: Governance requirements may become a common operating constraint.\n"
                    "Watch: Official legislative and enforcement updates."
                )
            elif term in {"chip", "semiconductor", "supply", "export", "tariff"}:
                insights.append(
                    "Pattern: Hardware and trade constraints overlap across reporting lines.\n"
                    "Why it matters: Supply and pricing conditions may shift across technology sectors.\n"
                    "Watch: Export-control notices and manufacturing guidance updates."
                )
            elif term in {"conflict", "security", "sanction", "military"}:
                insights.append(
                    "Pattern: Security-driven developments recur across stories.\n"
                    "Why it matters: Institutional risk posture may tighten in parallel domains.\n"
                    "Watch: Verified official statements and follow-up reporting."
                )

        if not insights:
            insights.append(
                "Pattern: Multiple stories indicate concurrent structural change.\n"
                "Why it matters: Cross-domain planning assumptions may need review.\n"
                "Watch: Primary-source follow-up over the next reporting cycle."
            )

        return insights[:3]

    def _narrative_threads(
        self,
        headlines: list[dict[str, Any]],
        developing_stories: list[dict[str, Any]] | None = None,
    ) -> list[str]:
        cluster_counts: dict[str, int] = {}
        for item in headlines[:9]:
            label = self._cluster_label(item)
            cluster_counts[label] = cluster_counts.get(label, 0) + 1

        tracked_updates: dict[str, int] = {}
        for story in (developing_stories or [])[:12]:
            topic = str(story.get("topic") or "").strip()
            if not topic:
                continue
            tracked_updates[topic.lower()] = int(story.get("updates") or 0)

        ranked = sorted(cluster_counts.items(), key=lambda kv: kv[1], reverse=True)[:3]
        threads: list[str] = []
        for label, count in ranked:
            label_text = label.title()
            matched_updates = 0
            for topic_lower, updates in tracked_updates.items():
                if any(token in topic_lower for token in re.findall(r"[a-zA-Z]{4,}", label.lower())):
                    matched_updates = max(matched_updates, updates)
            if matched_updates <= 0:
                # Fallback to headline-level evolution markers when no explicit tracker topic matches.
                matched_updates = max(
                    [
                        int(item.get("evolution_cycles") or 0)
                        for item in headlines
                        if self._cluster_label(item) == label
                    ]
                    or [0]
                )

            trajectory = (
                f"This thread appears in {count} current stories and shows {matched_updates} tracked updates."
                if matched_updates > 0
                else f"This thread appears in {count} current stories with no prior tracked updates yet."
            )

            threads.append(
                f"Thread: {label_text}\n"
                f"Trajectory: {trajectory}\n"
                "Watch: Confirm the next official update before revising assumptions."
            )

        if not threads:
            threads.append(
                "Thread: General Developments\n"
                "Trajectory: Current stories remain distributed across unrelated domains.\n"
                "Watch: Monitor the next cycle for convergence."
            )
        return threads

    def render_brief(
        self,
        headlines: list[dict[str, Any]],
        analysis_text: str = "",
        developing_stories: list[dict[str, Any]] | None = None,
    ) -> str:
        if not headlines:
            return "No news data available."

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        strategic_snapshot = self._strategic_snapshot(headlines)
        lines = [
            "NOVA INTELLIGENCE BRIEF",
            "Daily Situation Overview",
            "------------------------",
            f"Generated: {ts}",
            f"Stories analyzed: {len(headlines[:9])}",
            "",
            f"Bottom line: {self._bottom_line(analysis_text, fallback=strategic_snapshot)}",
            "",
            "Strategic Snapshot",
            "------------------",
            strategic_snapshot,
            "",
            "Cross-Story Insights",
            "--------------------",
        ]

        for insight in self._cross_story_insights(headlines):
            lines.extend(["", insight])

        lines.extend(
            [
                "",
                "Narrative Threads",
                "-----------------",
            ]
        )

        for thread in self._narrative_threads(headlines, developing_stories):
            lines.extend(["", thread])

        lines.extend(
            [
                "",
                "Topic Clusters",
            ]
        )

        clusters: dict[str, list[dict[str, Any]]] = {}
        for item in headlines[:9]:
            label = self._cluster_label(item)
            clusters.setdefault(label, []).append(item)

        for label, items in clusters.items():
            lines.append("")
            lines.append(label)
            for item in items[:3]:
                title = (item.get("title") or "Unknown").strip()
                lines.append(f"- {title}")

        if analysis_text.strip():
            lines.extend(["", "Analyst Note", analysis_text.strip()])

        lines.extend(["", "Detailed Story Briefs", "---------------------"])
        for idx, item in enumerate(headlines[:5], start=1):
            title = (item.get("title") or "Unknown").strip()
            source = (item.get("source") or "Unknown").strip()
            summary = (item.get("summary") or title).strip()
            seed = f"{title}. {summary}"
            importance, confidence = self._importance_confidence(seed, source)

            lines.extend(
                [
                    "",
                    f"{idx}. {title}",
                    f"Source: {source}",
                    "",
                    "Summary",
                    summary,
                    "",
                    "Signal",
                    self._derive_signal(seed),
                    "",
                    "Implication",
                    self._derive_implication(seed),
                    "",
                    "Watch",
                    self._derive_watch(seed),
                    "",
                    f"Importance: {importance}",
                    f"Confidence: {confidence}",
                ]
            )
            evolution_cycles = item.get("evolution_cycles")
            if isinstance(evolution_cycles, int) and evolution_cycles > 1:
                lines.append(f"Evolution: This story has developed across {evolution_cycles} reporting cycles.")

        if developing_stories:
            lines.extend(["", "Developing Stories", "------------------"])
            for story in developing_stories[:6]:
                topic = str(story.get("topic") or "Unknown")
                cycles = int(story.get("updates", 0))
                lines.append(f"- {topic} ({cycles} updates tracked)")

        return "\n".join(lines)

    def render_single(self, headline: dict[str, Any], analysis_text: str = "") -> str:
        title = (headline.get("title") or "Unknown").strip()
        source = (headline.get("source") or "Unknown").strip()
        url = (headline.get("url") or "").strip()
        summary = (headline.get("summary") or "").strip()
        context = analysis_text.strip() or summary or "Limited detail is available from the selected headline."

        lines = [
            "DETAILED STORY ANALYSIS",
            "-----------------------",
            f"Title: {title}",
            f"Source: {source}",
        ]
        if url:
            lines.append(f"Reference: {url}")

        seed = f"{title}. {analysis_text or summary}"
        importance, confidence = self._importance_confidence(seed, source)
        lines.extend(
            [
                "",
                f"Bottom line: {self._bottom_line(context, fallback=self._derive_signal(seed))}",
                "",
                "Summary",
                context,
                "",
                "Signal",
                self._derive_signal(seed),
                "",
                "Implication",
                self._derive_implication(seed),
                "",
                "Watch",
                self._derive_watch(seed),
                "",
                f"Importance: {importance}",
                f"Confidence: {confidence}",
            ]
        )

        evolution_cycles = headline.get("evolution_cycles")
        if isinstance(evolution_cycles, int) and evolution_cycles > 1:
            lines.append(f"Evolution: This story has developed across {evolution_cycles} reporting cycles.")

        return "\n".join(lines)

    def render_multi_source_report(
        self,
        query: str,
        findings: list[str],
        sources: list[str],
        analysis_text: str = "",
    ) -> str:
        query_text = (query or "").strip() or "report query"
        selected_findings = [f.strip() for f in findings if str(f).strip()][:5]
        selected_sources = [s.strip() for s in sources if str(s).strip()][:5]

        if not selected_findings:
            selected_findings = ["No reliable findings were returned for this query."]
        if not selected_sources:
            selected_sources = ["multiple sources"]

        seed = " ".join(selected_findings)
        lines = [
            "NOVA MULTI-SOURCE REPORT",
            "------------------------",
            f"Query: {query_text}",
            "",
            f"Bottom line: {self._bottom_line(analysis_text, fallback=selected_findings[0])}",
            "",
            "Strategic Snapshot",
            self._strategic_snapshot([{"title": item, "summary": item} for item in selected_findings]),
            "",
            "Top Findings",
        ]
        lines.extend(f"- {item}" for item in selected_findings)
        lines.extend(
            [
                "",
                "Cross-Story Insight",
                f"Signal: {self._derive_signal(seed)}",
                f"Implication: {self._derive_implication(seed)}",
                f"Watch: {self._derive_watch(seed)}",
                "",
                "Sources",
            ]
        )
        lines.extend(f"- {src}" for src in selected_sources)
        if analysis_text.strip():
            lines.extend(["", "Analyst Note", analysis_text.strip()])
        return "\n".join(lines)

    def render_structured_intelligence_brief(
        self,
        *,
        topic: str,
        summary: str,
        key_findings: list[str],
        supporting_sources: list[str],
        contradictions: list[str],
        confidence: float,
        source_credibility: list[dict[str, Any]] | None = None,
        confidence_factors: dict[str, float] | None = None,
        counter_analysis: str = "",
    ) -> str:
        clean_topic = (topic or "").strip() or "General Topic"
        clean_summary = (summary or "").strip() or "No summary available."
        clean_findings = [str(item).strip() for item in (key_findings or []) if str(item).strip()] or [
            "No high-confidence findings available."
        ]
        clean_sources = [str(item).strip() for item in (supporting_sources or []) if str(item).strip()] or [
            "No source attribution available."
        ]
        clean_contradictions = [str(item).strip() for item in (contradictions or []) if str(item).strip()] or [
            "No major contradiction markers detected."
        ]
        credibility_rows = list(source_credibility or [])
        factors = dict(confidence_factors or {})
        clean_counter = str(counter_analysis or "").strip() or (
            "Counter-view: available evidence may still contain unresolved uncertainty."
        )
        bounded_confidence = max(0.0, min(1.0, float(confidence)))

        lines = [
            "INTELLIGENCE BRIEF",
            f"Topic: {clean_topic}",
            "",
            f"Bottom line: {self._bottom_line(clean_summary)}",
            "",
            "Summary",
            "-------",
            clean_summary,
            "",
            "Key Findings",
            "------------",
        ]
        lines.extend(f"- {item}" for item in clean_findings[:5])
        lines.extend(
            [
                "",
                "Supporting Sources",
                "------------------",
            ]
        )
        lines.extend(f"{idx}. {item}" for idx, item in enumerate(clean_sources[:5], start=1))
        lines.extend(
            [
                "",
                "Contradictions",
                "--------------",
            ]
        )
        lines.extend(f"- {item}" for item in clean_contradictions[:4])
        lines.extend(
            [
                "",
                "Confidence",
                "----------",
                f"{bounded_confidence:.2f}",
            ]
        )
        lines.extend(
            [
                "",
                "Source Credibility",
                "------------------",
            ]
        )
        if credibility_rows:
            for idx, row in enumerate(credibility_rows[:6], start=1):
                source = str(row.get("source") or "unknown-source").strip()
                classification = str(row.get("classification") or "unknown").strip().lower()
                score = max(0.0, min(1.0, float(row.get("score", 0.50))))
                lines.append(f"{idx}. {source} | {classification} | {score:.2f}")
        else:
            lines.append("1. unattributed-source | unknown | 0.50")

        lines.extend(
            [
                "",
                "Confidence Factors",
                "------------------",
            ]
        )
        if factors:
            ordered = (
                "source_agreement",
                "source_credibility",
                "data_freshness",
                "verification_alignment",
                "factor_model",
            )
            for key in ordered:
                if key in factors:
                    val = max(0.0, min(1.0, float(factors[key])))
                    lines.append(f"- {key}: {val:.2f}")
        else:
            lines.extend(
                [
                    "- source_agreement: 0.50",
                    "- source_credibility: 0.50",
                    "- data_freshness: 0.50",
                ]
            )

        lines.extend(
            [
                "",
                "Counter Analysis",
                "----------------",
                clean_counter,
            ]
        )
        return "\n".join(lines)
