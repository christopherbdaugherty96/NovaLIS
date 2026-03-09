from __future__ import annotations

import os
from typing import Any

from src.actions.action_result import ActionResult
from src.cognition.cognitive_layer_contract import CognitiveMode, CognitiveRequest
from src.cognition.intelligence_report_contract import (
    validate_rendered_report_text,
    validate_structured_report_payload,
)
from src.cognition.modules import ReportingModule, ResearchModule, VerificationModule
from src.conversation.deepseek_bridge import DeepSeekBridge
from src.conversation.deepseek_safety_wrapper import DeepSeekSafetyWrapper
from src.llm.llm_gateway import generate_chat
from src.rendering.intelligence_brief_renderer import IntelligenceBriefRenderer
from src.validation.pipeline import ValidationPipeline

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
DUCK_SEARCH_URL = "https://api.duckduckgo.com/"


class MultiSourceReportingExecutor:
    """Single-invocation multi-source reporting built on governed search endpoint."""

    def __init__(self, network):
        self.network = network
        self.renderer = IntelligenceBriefRenderer()
        self.validation_pipeline = ValidationPipeline()
        self.research_module = ResearchModule()
        self.verification_module = VerificationModule()
        self.reporting_module = ReportingModule()
        self.deepseek_bridge = DeepSeekBridge()
        self.deepseek_safety = DeepSeekSafetyWrapper()

    @staticmethod
    def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
        return max(lower, min(upper, float(value)))

    @staticmethod
    def _extract_domain(url: str) -> str:
        raw = str(url or "").strip().lower()
        if not raw:
            return ""
        domain = raw.split("//")[-1].split("/")[0].strip()
        if domain.startswith("www."):
            return domain[4:]
        return domain

    @classmethod
    def _classify_source(cls, domain: str, title: str = "") -> str:
        dom = str(domain or "").strip().lower()
        title_text = str(title or "").strip().lower()
        if not dom:
            return "unknown"

        if dom.endswith(".gov") or dom.endswith(".edu"):
            return "primary"

        primary_domains = (
            "reuters.com",
            "apnews.com",
            "whitehouse.gov",
            "sec.gov",
            "congress.gov",
            "europa.eu",
            "who.int",
            "imf.org",
            "worldbank.org",
        )
        if any(dom == p or dom.endswith(f".{p}") for p in primary_domains):
            return "primary"

        opinion_markers = ("opinion", "editorial", "blog", "substack", "medium.com", "op-ed")
        if any(marker in dom for marker in opinion_markers) or any(marker in title_text for marker in opinion_markers):
            return "opinion"

        secondary_domains = (
            "bbc.com",
            "npr.org",
            "nytimes.com",
            "wsj.com",
            "ft.com",
            "bloomberg.com",
            "axios.com",
            "cnbc.com",
            "theverge.com",
            "wikipedia.org",
        )
        if any(dom == s or dom.endswith(f".{s}") for s in secondary_domains):
            return "secondary"

        return "secondary"

    @staticmethod
    def _credibility_score(classification: str) -> float:
        scores = {
            "primary": 0.95,
            "secondary": 0.72,
            "opinion": 0.35,
            "unknown": 0.50,
        }
        return scores.get(str(classification or "").strip().lower(), 0.50)

    @classmethod
    def _build_source_credibility(cls, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in results[:8]:
            domain = cls._extract_domain(item.get("url", ""))
            if not domain or domain in seen:
                continue
            seen.add(domain)
            classification = cls._classify_source(domain, title=item.get("title", ""))
            rows.append(
                {
                    "source": domain,
                    "classification": classification,
                    "score": round(cls._credibility_score(classification), 2),
                }
            )
        return rows

    @classmethod
    def _estimate_freshness(cls, query: str, results: list[dict[str, Any]]) -> float:
        freshness_markers = ("published", "published_at", "date", "updated", "age", "page_age", "last_modified")
        marker_hits = 0
        for item in results[:8]:
            if any(item.get(marker) for marker in freshness_markers):
                marker_hits += 1

        query_hint = 0.0
        lowered_query = str(query or "").lower()
        if any(k in lowered_query for k in ("today", "latest", "recent", "current")):
            query_hint = 0.05

        if marker_hits >= 3:
            return cls._clamp(0.82 + query_hint)
        if marker_hits >= 1:
            return cls._clamp(0.72 + query_hint)
        return cls._clamp(0.60 + query_hint)

    @classmethod
    def _compute_confidence_factors(
        cls,
        *,
        query: str,
        results: list[dict[str, Any]],
        source_credibility: list[dict[str, Any]],
        contradictions: list[str],
        verification_confidence: float,
    ) -> tuple[float, dict[str, float]]:
        unique_sources = {
            cls._extract_domain(item.get("url", ""))
            for item in results[:8]
            if cls._extract_domain(item.get("url", ""))
        }
        source_count = len(unique_sources)
        agreement = 0.40 + min(source_count, 5) * 0.10
        contradiction_penalty = min(0.24, max(0, len(contradictions)) * 0.08)
        source_agreement = cls._clamp(agreement - contradiction_penalty)

        if source_credibility:
            source_credibility_score = sum(float(row.get("score", 0.5)) for row in source_credibility) / len(source_credibility)
        else:
            source_credibility_score = 0.50
        source_credibility_score = cls._clamp(source_credibility_score)

        data_freshness = cls._estimate_freshness(query, results)
        factor_confidence = cls._clamp(
            0.45 * source_agreement
            + 0.35 * source_credibility_score
            + 0.20 * data_freshness
        )
        final_confidence = cls._clamp(0.75 * factor_confidence + 0.25 * cls._clamp(verification_confidence))
        factor_map = {
            "source_agreement": round(source_agreement, 2),
            "source_credibility": round(source_credibility_score, 2),
            "data_freshness": round(data_freshness, 2),
            "verification_alignment": round(cls._clamp(verification_confidence), 2),
            "factor_model": round(factor_confidence, 2),
        }
        return round(final_confidence, 2), factor_map

    def _build_counter_analysis(self, query: str, findings: list[str]) -> str:
        prompt = (
            "Provide one short counter-analysis paragraph that challenges the main narrative.\n"
            "Stay factual and bounded to uncertainty.\n"
            "Do not give instructions or recommendations.\n\n"
            f"Query: {query}\n"
            "Main findings:\n"
            + "\n".join(f"- {item}" for item in (findings or [])[:5])
        )
        try:
            raw = self.deepseek_bridge.analyze(prompt, [], suggested_max_tokens=240)
            sanitized = self.deepseek_safety.sanitize(raw)
            cleaned = " ".join(str(sanitized or "").split()).strip()
            if cleaned:
                return cleaned[:420]
        except Exception:
            pass
        return "Counter-view: available sources may be incomplete, so conclusions should remain provisional."

    @staticmethod
    def _parse_duck_results(data: dict[str, Any]) -> list[dict[str, Any]]:
        if not isinstance(data, dict):
            return []
        rows: list[dict[str, Any]] = []
        abstract = str(data.get("Abstract") or "").strip()
        abstract_url = str(data.get("AbstractURL") or "").strip()
        if abstract and abstract_url:
            rows.append({"title": abstract[:100], "url": abstract_url, "description": abstract[:200]})

        for topic in data.get("RelatedTopics") or []:
            if isinstance(topic, dict) and topic.get("FirstURL") and topic.get("Text"):
                rows.append(
                    {
                        "title": str(topic.get("Text") or "")[:100],
                        "url": str(topic.get("FirstURL") or "").strip(),
                        "description": str(topic.get("Text") or "")[:200],
                    }
                )
            if isinstance(topic, dict):
                for nested in topic.get("Topics") or []:
                    if isinstance(nested, dict) and nested.get("FirstURL") and nested.get("Text"):
                        rows.append(
                            {
                                "title": str(nested.get("Text") or "")[:100],
                                "url": str(nested.get("FirstURL") or "").strip(),
                                "description": str(nested.get("Text") or "")[:200],
                            }
                        )
        return rows

    def _fetch_governed_results(
        self,
        *,
        capability_id: int,
        query: str,
        request_id: str,
        session_id: str | None,
    ) -> tuple[list[dict[str, Any]], str]:
        brave_key = os.getenv("BRAVE_API_KEY")
        if brave_key:
            try:
                response = self.network.request(
                    capability_id=capability_id,
                    method="GET",
                    url=BRAVE_SEARCH_URL,
                    params={"q": query, "count": 5},
                    headers={"Accept": "application/json", "X-Subscription-Token": brave_key},
                    as_json=True,
                    timeout=5,
                    request_id=request_id,
                    session_id=session_id,
                )
                if int(response.get("status_code") or 0) == 200:
                    results = ((response.get("data") or {}).get("web") or {}).get("results") or []
                    if isinstance(results, list) and results:
                        return list(results), "brave"
            except Exception:
                pass

        try:
            response = self.network.request(
                capability_id=capability_id,
                method="GET",
                url=DUCK_SEARCH_URL,
                params={
                    "q": query,
                    "format": "json",
                    "no_html": "1",
                    "no_redirect": "1",
                    "skip_disambig": "1",
                },
                headers={"Accept": "application/json"},
                as_json=True,
                timeout=4,
                request_id=request_id,
                session_id=session_id,
            )
            if int(response.get("status_code") or 0) != 200:
                return [], "none"
            return self._parse_duck_results(response.get("data") or {}), "duckduckgo"
        except Exception:
            return [], "none"

    def execute(self, request) -> ActionResult:
        query = (request.params or {}).get("query", "").strip()
        session_id = str((request.params or {}).get("session_id") or "").strip() or None
        if not query:
            return ActionResult.failure("No report query provided.", request_id=request.request_id)

        results, provider = self._fetch_governed_results(
            capability_id=48,
            query=query,
            request_id=request.request_id,
            session_id=session_id,
        )
        if not results:
            return ActionResult.failure("I couldn't build the report due to a network issue.", request_id=request.request_id)
        top_results = list(results[:6])
        titles = [item.get("title", "").strip() for item in top_results if item.get("title")]
        domains = []
        for item in top_results:
            url = item.get("url", "")
            dom = url.split("//")[-1].split("/")[0].strip().lower()
            if dom and dom not in domains:
                domains.append(dom)

        analysis_text = generate_chat(
            "Create a short factual analyst note for this query using the findings.\n"
            f"Query: {query}\n"
            "Findings:\n"
            + "\n".join(f"- {item}" for item in titles)
            + "\n"
            "Avoid directives. Keep to 2-4 lines.",
            mode="analysis_only",
            safety_profile="analysis",
            request_id=f"{request.request_id}:multi_source",
            session_id=session_id,
            max_tokens=220,
            temperature=0.2,
        )
        research_result = self.research_module.analyze(
            CognitiveRequest(
                user_query=query,
                mode=CognitiveMode.ANALYSIS,
                request_id=request.request_id,
                source_data={"web_results": top_results},
            )
        )

        verification_result = self.verification_module.analyze(
            CognitiveRequest(
                user_query=query,
                mode=CognitiveMode.VERIFICATION,
                request_id=request.request_id,
                source_data={
                    "findings": list(research_result.key_points),
                    "sources": list(research_result.supporting_sources),
                },
            )
        )

        reporting_result = self.reporting_module.analyze(
            CognitiveRequest(
                user_query=query,
                mode=CognitiveMode.REPORTING,
                request_id=request.request_id,
                source_data={
                    "summary": (analysis_text or "").strip() or research_result.summary,
                    "findings": list(research_result.key_points),
                    "sources": list(research_result.supporting_sources),
                    "contradictions": list(verification_result.diagnostics.get("contradictions", [])),
                    "confidence": verification_result.confidence,
                },
            )
        )

        contradictions = list(reporting_result.diagnostics.get("contradictions", []))
        source_credibility = self._build_source_credibility(top_results)
        confidence_score, confidence_factors = self._compute_confidence_factors(
            query=query,
            results=top_results,
            source_credibility=source_credibility,
            contradictions=contradictions,
            verification_confidence=float(verification_result.confidence),
        )
        counter_analysis = self._build_counter_analysis(
            query=query,
            findings=list(reporting_result.key_points),
        )

        structured_brief = {
            "topic": query,
            "summary": reporting_result.summary,
            "key_findings": list(reporting_result.key_points),
            "supporting_sources": list(reporting_result.supporting_sources),
            "contradictions": contradictions,
            "confidence": confidence_score,
            "source_credibility": source_credibility,
            "confidence_factors": confidence_factors,
            "counter_analysis": counter_analysis,
        }

        contract_status = "pass"
        validation_status = "pass"
        fallback_reason = ""
        try:
            validate_structured_report_payload(structured_brief)
            message = self.renderer.render_structured_intelligence_brief(
                topic=structured_brief["topic"][:140],
                summary=structured_brief["summary"],
                key_findings=structured_brief["key_findings"],
                supporting_sources=structured_brief["supporting_sources"],
                contradictions=structured_brief["contradictions"],
                confidence=structured_brief["confidence"],
                source_credibility=structured_brief["source_credibility"],
                confidence_factors=structured_brief["confidence_factors"],
                counter_analysis=structured_brief["counter_analysis"],
            )
            validate_rendered_report_text(message)
            validation = self.validation_pipeline.validate(reporting_result.summary, message)
            if not validation.ok:
                validation_status = "fail"
                raise ValueError(f"validation_pipeline_failed:{validation.stage}:{validation.reason}")
        except Exception as exc:
            contract_status = "fail"
            fallback_reason = str(exc)
            fallback_structured = {
                "topic": query,
                "summary": "Report generated with fallback due to contract validation safeguards.",
                "key_findings": [
                    "Primary report output did not satisfy structured contract checks.",
                    "Fallback sections are rendered to preserve deterministic report shape.",
                ],
                "supporting_sources": domains[:5] or ["unattributed-source"],
                "contradictions": ["Contract validation fallback was applied for this response."],
                "confidence": 0.40,
                "source_credibility": source_credibility or [{"source": "unattributed-source", "classification": "unknown", "score": 0.5}],
                "confidence_factors": {
                    "source_agreement": 0.40,
                    "source_credibility": 0.50,
                    "data_freshness": 0.50,
                    "verification_alignment": 0.40,
                    "factor_model": 0.44,
                },
                "counter_analysis": "Counter-view: fallback path was used due to report validation safeguards.",
            }
            structured_brief = fallback_structured
            message = self.renderer.render_structured_intelligence_brief(
                topic=fallback_structured["topic"][:140],
                summary=fallback_structured["summary"],
                key_findings=fallback_structured["key_findings"],
                supporting_sources=fallback_structured["supporting_sources"],
                contradictions=fallback_structured["contradictions"],
                confidence=fallback_structured["confidence"],
                source_credibility=fallback_structured["source_credibility"],
                confidence_factors=fallback_structured["confidence_factors"],
                counter_analysis=fallback_structured["counter_analysis"],
            )
            validate_rendered_report_text(message)

        widget_results = [{"title": i.get("title", "")[:100], "url": i.get("url", "")} for i in results[:5]]
        return ActionResult.ok(
            message=message,
            data={
                "widget": {"type": "search", "data": {"results": widget_results}},
                "structured_brief": {
                    **structured_brief,
                    "search_provider": provider,
                    "contract_status": contract_status,
                    "validation_status": validation_status,
                    "fallback_reason": fallback_reason,
                },
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )
