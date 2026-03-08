from __future__ import annotations

from src.cognition.cognitive_layer_contract import (
    CognitiveModule,
    CognitiveRequest,
    CognitiveResult,
    validate_cognitive_result,
)


class ResearchModule(CognitiveModule):
    """Template analysis-only research module for Phase 4.2 cognition surfaces."""

    name = "research_module"
    version = "0.1.0"

    def analyze(self, request: CognitiveRequest) -> CognitiveResult:
        topic = request.user_query.strip() or "General Topic"
        web_results = request.source_data.get("web_results", [])
        findings: list[str] = []
        sources: list[str] = []

        if isinstance(web_results, list):
            for item in web_results[:6]:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title") or "").strip()
                description = str(item.get("description") or "").strip()
                url = str(item.get("url") or "").strip()
                if title:
                    findings.append(f"{title}{': ' + description if description else ''}")
                if url:
                    domain = url.split("//")[-1].split("/")[0].strip().lower()
                    if domain and domain not in sources:
                        sources.append(domain)

        if not findings:
            findings = ["No reliable findings were returned for this topic."]
        if not sources:
            sources = ["unattributed-source"]

        summary = (
            f"Research scan for '{topic}' identified {len(findings)} finding(s) "
            f"across {len(sources)} source domain(s)."
        )
        key_points = (
            *tuple(findings[:5]),
        )
        result = CognitiveResult(
            summary=summary,
            key_points=key_points,
            supporting_sources=tuple(sources[:5]),
            confidence=0.65 if len(findings) >= 3 else 0.5,
            module_name=self.name,
            diagnostics={
                "template": True,
                "topic": topic,
                "findings": findings[:5],
                "source_count": len(sources),
                "request_id": request.request_id,
            },
        )
        validate_cognitive_result(result)
        return result
