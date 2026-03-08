from __future__ import annotations

import os

from src.actions.action_result import ActionResult
from src.cognition.cognitive_layer_contract import CognitiveMode, CognitiveRequest
from src.cognition.intelligence_report_contract import (
    validate_rendered_report_text,
    validate_structured_report_payload,
)
from src.cognition.modules import ReportingModule, ResearchModule, VerificationModule
from src.llm.llm_gateway import generate_chat
from src.rendering.intelligence_brief_renderer import IntelligenceBriefRenderer
from src.validation.pipeline import ValidationPipeline


class MultiSourceReportingExecutor:
    """Single-invocation multi-source reporting built on governed search endpoint."""

    def __init__(self, network):
        self.network = network
        self.renderer = IntelligenceBriefRenderer()
        self.validation_pipeline = ValidationPipeline()
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

        structured_brief = {
            "topic": query,
            "summary": reporting_result.summary,
            "key_findings": list(reporting_result.key_points),
            "supporting_sources": list(reporting_result.supporting_sources),
            "contradictions": list(reporting_result.diagnostics.get("contradictions", [])),
            "confidence": reporting_result.confidence,
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
            }
            structured_brief = fallback_structured
            message = self.renderer.render_structured_intelligence_brief(
                topic=fallback_structured["topic"][:140],
                summary=fallback_structured["summary"],
                key_findings=fallback_structured["key_findings"],
                supporting_sources=fallback_structured["supporting_sources"],
                contradictions=fallback_structured["contradictions"],
                confidence=fallback_structured["confidence"],
            )
            validate_rendered_report_text(message)

        widget_results = [{"title": i.get("title", "")[:100], "url": i.get("url", "")} for i in results[:5]]
        return ActionResult.ok(
            message=message,
            data={
                "widget": {"type": "search", "data": {"results": widget_results}},
                "structured_brief": {
                    **structured_brief,
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
