from __future__ import annotations

import os

from src.actions.action_result import ActionResult
from src.cognition.cognitive_layer_contract import CognitiveMode, CognitiveRequest
from src.cognition.modules import ReportingModule, ResearchModule, VerificationModule
from src.llm.llm_gateway import generate_chat
from src.rendering.intelligence_brief_renderer import IntelligenceBriefRenderer


class MultiSourceReportingExecutor:
    """Single-invocation multi-source reporting built on governed search endpoint."""

    def __init__(self, network):
        self.network = network
        self.renderer = IntelligenceBriefRenderer()
        self.research_module = ResearchModule()
        self.verification_module = VerificationModule()
        self.reporting_module = ReportingModule()

    def execute(self, request) -> ActionResult:
        query = (request.params or {}).get("query", "").strip()
        if not query:
            return ActionResult.failure("No report query provided.", request_id=request.request_id)

        brave_key = os.getenv("BRAVE_API_KEY")
        if not brave_key:
            return ActionResult.failure("Search service is not configured.", request_id=request.request_id)

        try:
            response = self.network.request(
                capability_id=48,
                method="GET",
                url="https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": 5},
                headers={"Accept": "application/json", "X-Subscription-Token": brave_key},
                as_json=True,
                timeout=5,
            )
        except Exception:
            return ActionResult.failure("I couldn't build the report due to a network issue.", request_id=request.request_id)

        if response.get("status_code") != 200:
            return ActionResult.failure("I couldn't build the report right now.", request_id=request.request_id)

        results = ((response.get("data") or {}).get("web") or {}).get("results") or []
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

        message = self.renderer.render_structured_intelligence_brief(
            topic=query[:140],
            summary=reporting_result.summary,
            key_findings=list(reporting_result.key_points),
            supporting_sources=list(reporting_result.supporting_sources),
            contradictions=list(reporting_result.diagnostics.get("contradictions", [])),
            confidence=reporting_result.confidence,
        )

        widget_results = [{"title": i.get("title", "")[:100], "url": i.get("url", "")} for i in results[:5]]
        return ActionResult.ok(
            message=message,
            data={
                "widget": {"type": "search", "data": {"results": widget_results}},
                "structured_brief": {
                    "topic": query,
                    "summary": reporting_result.summary,
                    "key_findings": list(reporting_result.key_points),
                    "supporting_sources": list(reporting_result.supporting_sources),
                    "contradictions": list(reporting_result.diagnostics.get("contradictions", [])),
                    "confidence": reporting_result.confidence,
                },
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )
