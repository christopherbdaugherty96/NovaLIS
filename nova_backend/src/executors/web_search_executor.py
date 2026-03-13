# src/executors/web_search_executor.py

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from src.actions.action_result import ActionResult
from src.conversation.response_style_router import ResponseTemplates
from src.llm.llm_gateway import generate_chat
from src.utils.content_extractor import extract_text_from_html

logger = logging.getLogger(__name__)

SEARCH_HARD_TIMEOUT_SECONDS = 7.0
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
DUCK_SEARCH_URL = "https://api.duckduckgo.com/"
MAX_SOURCE_READS = 3
SOURCE_READ_TIMEOUT_SECONDS = 2.5
MAX_SOURCE_TEXT_CHARS = 2800
SYNTHESIS_TIMEOUT_SECONDS = 4.2


class WebSearchExecutor:
    _avg_latency_seconds = 0.0
    _latency_samples = 0

    """
    Executes a governed web search using the Brave Search API.
    All outbound HTTP is routed through NetworkMediator.
    """

    def __init__(self, network, execute_boundary):
        self.network = network
        self.execute_boundary = execute_boundary

    @staticmethod
    def _format_provider_label(provider: str) -> str:
        if provider == "brave":
            return "Brave Search"
        if provider == "duckduckgo":
            return "DuckDuckGo Instant Answer"
        return "Unknown"

    @staticmethod
    def _build_summary(query: str, results: list[dict]) -> str:
        if not results:
            return ""
        top = [r.get("title", "").strip() for r in results[:2] if (r.get("title") or "").strip()]
        if not top:
            return f'Results found for "{query}".'
        if len(top) == 1:
            return f'Top result for "{query}": {top[0]}.'
        return f'Top results for "{query}": {top[0]}; {top[1]}.'

    @staticmethod
    def _build_suggested_actions() -> list[dict]:
        return [
            {"label": "Summarize results", "prompt": "summarize these search results"},
            {"label": "Compare top results", "prompt": "compare the top 3 search results"},
            {"label": "Most reliable source", "prompt": "which result is the most reliable source and why"},
        ]

    @classmethod
    def _follow_up_prompts(cls) -> list[str]:
        return [item["prompt"] for item in cls._build_suggested_actions()]

    def _empty_widget(
        self,
        query: str = "",
        provider: str = "",
        latency_seconds: float = 0.0,
        *,
        researched_summary: str = "",
        source_pages_read: int = 0,
    ) -> dict:
        return {
            "widget": {
                "type": "search",
                "data": {
                    "query": query,
                    "provider": self._format_provider_label(provider),
                    "latency_seconds": latency_seconds,
                    "result_count": 0,
                    "summary": researched_summary,
                    "researched_summary": researched_summary,
                    "source_pages_read": source_pages_read,
                    "follow_up_prompts": self._follow_up_prompts(),
                    "suggested_actions": self._build_suggested_actions(),
                    "results": [],
                },
            }
        }

    def _search_widget(
        self,
        query: str,
        provider: str,
        latency_seconds: float,
        results: list[dict],
        *,
        researched_summary: str = "",
        source_pages_read: int = 0,
    ) -> dict:
        widget_summary = (researched_summary or "").strip() or self._build_summary(query, results)
        return {
            "widget": {
                "type": "search",
                "data": {
                    "query": query,
                    "provider": self._format_provider_label(provider),
                    "latency_seconds": round(latency_seconds, 2),
                    "result_count": len(results),
                    "summary": widget_summary,
                    "researched_summary": widget_summary,
                    "source_pages_read": source_pages_read,
                    "follow_up_prompts": self._follow_up_prompts(),
                    "suggested_actions": self._build_suggested_actions(),
                    "results": results,
                },
            }
        }

    @classmethod
    def _record_latency(cls, elapsed_seconds: float) -> float:
        cls._latency_samples += 1
        if cls._latency_samples == 1:
            cls._avg_latency_seconds = elapsed_seconds
        else:
            cls._avg_latency_seconds = ((cls._avg_latency_seconds * (cls._latency_samples - 1)) + elapsed_seconds) / cls._latency_samples
        return cls._avg_latency_seconds

    @staticmethod
    def _extract_domain(url: str) -> str:
        return (url or "").split("//")[-1].split("/")[0].strip().lower()

    def _parse_results(self, data: dict) -> list[dict]:
        # Brave format
        web_results = ((data.get("web") or {}).get("results") or []) if isinstance(data, dict) else []
        if web_results:
            out = []
            for item in web_results:
                out.append(
                    {
                        "title": (item.get("title") or "")[:100],
                        "url": item.get("url", ""),
                        "snippet": (item.get("description") or "")[:200],
                    }
                )
            return out

        # Legacy Duck style used by tests
        out = []
        abstract = (data.get("Abstract") or "").strip() if isinstance(data, dict) else ""
        abstract_url = (data.get("AbstractURL") or "").strip() if isinstance(data, dict) else ""
        if abstract and abstract_url:
            title = (abstract[:99] + "...") if len(abstract) > 100 else abstract
            out.append({"title": title, "url": abstract_url, "snippet": abstract[:200]})

        for topic in (data.get("RelatedTopics") or []) if isinstance(data, dict) else []:
            if isinstance(topic, dict) and topic.get("FirstURL") and topic.get("Text"):
                out.append({"title": topic["Text"][:100], "url": topic["FirstURL"], "snippet": topic["Text"][:200]})
            for sub in topic.get("Topics", []) if isinstance(topic, dict) else []:
                if isinstance(sub, dict) and sub.get("FirstURL") and sub.get("Text"):
                    out.append({"title": sub["Text"][:100], "url": sub["FirstURL"], "snippet": sub["Text"][:200]})

        return out

    def _search_duckduckgo(self, request, query: str, session_id: str | None):
        try:
            return self.network.request(
                capability_id=request.capability_id,
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
                request_id=request.request_id,
                session_id=session_id,
            )
        except Exception as error:
            if error.__class__.__name__ == "NetworkMediatorError":
                return None
            raise

    def _fetch_source_text(
        self,
        *,
        capability_id: int,
        url: str,
        request_id: str | None,
        session_id: str | None,
    ) -> str:
        cleaned_url = str(url or "").strip()
        if not cleaned_url:
            return ""
        try:
            response = self.network.request(
                capability_id=capability_id,
                method="GET",
                url=cleaned_url,
                as_json=False,
                timeout=SOURCE_READ_TIMEOUT_SECONDS,
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
        *,
        capability_id: int,
        results: list[dict],
        request_id: str | None,
        session_id: str | None,
    ) -> list[dict]:
        candidates: list[dict] = []
        seen_urls: set[str] = set()
        for item in results:
            url = str(item.get("url") or "").strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            candidates.append(item)
            if len(candidates) >= MAX_SOURCE_READS:
                break

        if not candidates:
            return []

        packets: list[dict] = []
        worker_count = min(3, len(candidates))
        pool = ThreadPoolExecutor(max_workers=worker_count)
        futures = [
            (
                item,
                pool.submit(
                    self._fetch_source_text,
                    capability_id=capability_id,
                    url=str(item.get("url") or ""),
                    request_id=request_id,
                    session_id=session_id,
                ),
            )
            for item in candidates
        ]
        try:
            for item, future in futures:
                try:
                    text = (future.result(timeout=SOURCE_READ_TIMEOUT_SECONDS + 0.5) or "").strip()
                except FuturesTimeoutError:
                    future.cancel()
                    text = ""
                if not text:
                    continue
                packets.append(
                    {
                        "title": str(item.get("title") or "").strip(),
                        "url": str(item.get("url") or "").strip(),
                        "domain": self._extract_domain(str(item.get("url") or "")),
                        "text": text,
                    }
                )
        finally:
            pool.shutdown(wait=True, cancel_futures=True)
        return packets

    @staticmethod
    def _research_fallback(query: str, results: list[dict], source_packets: list[dict]) -> str:
        if source_packets:
            leads = [p.get("title", "").strip() for p in source_packets[:2] if p.get("title")]
            if len(leads) >= 2:
                return (
                    f'Across multiple sources on "{query}", the top reports align on {leads[0]} and {leads[1]}. '
                    "Details vary by outlet, so use the linked sources for full context."
                )
            if len(leads) == 1:
                return (
                    f'Based on reviewed source pages for "{query}", the central reported development is {leads[0]}. '
                    "Compare at least one additional source before final conclusions."
                )

        snippets = [str(item.get("snippet") or "").strip() for item in results[:3] if str(item.get("snippet") or "").strip()]
        if snippets:
            merged = " ".join(snippets)
            merged = " ".join(merged.split()).strip()
            if len(merged) > 340:
                merged = merged[:337].rstrip() + "..."
            return f'Based on available web snippets for "{query}": {merged}'
        return f'I found online sources for "{query}", but there was limited extractable detail to synthesize reliably.'

    def _synthesize_researched_summary(
        self,
        *,
        query: str,
        results: list[dict],
        source_packets: list[dict],
        request_id: str,
        session_id: str | None,
    ) -> str:
        fallback = self._research_fallback(query, results, source_packets)
        if not source_packets:
            return fallback

        source_blocks = []
        for idx, packet in enumerate(source_packets, start=1):
            source_blocks.append(
                f"[{idx}] {packet.get('title', '')}\n"
                f"Domain: {packet.get('domain', 'unknown')}\n"
                f"URL: {packet.get('url', '')}\n"
                f"Excerpt: {str(packet.get('text', ''))[:1200]}"
            )
        prompt = (
            "You are generating a source-grounded answer from web excerpts.\n"
            "Rules:\n"
            "- Use only provided excerpts.\n"
            "- Do not invent missing facts.\n"
            "- Keep to one concise paragraph (4-7 sentences).\n"
            "- Mention uncertainty if sources disagree or detail is limited.\n"
            "- Include source attribution in-text using domains when making key claims.\n\n"
            f"User query: {query}\n\n"
            "Source excerpts:\n"
            + "\n\n".join(source_blocks)
        )

        def _generate() -> str:
            return (
                generate_chat(
                    prompt,
                    mode="analysis_only",
                    safety_profile="analysis",
                    request_id=f"{request_id}:researched_search",
                    session_id=session_id,
                    max_tokens=260,
                    temperature=0.2,
                )
                or ""
            )

        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(_generate)
        try:
            text = (future.result(timeout=SYNTHESIS_TIMEOUT_SECONDS) or "").strip()
            if not text:
                return fallback
            return " ".join(text.split())
        except FuturesTimeoutError:
            future.cancel()
            return fallback
        except Exception:
            return fallback
        finally:
            pool.shutdown(wait=True, cancel_futures=True)

    def execute(self, request) -> ActionResult:
        query = request.params.get("query", "").strip()
        session_id = str(request.params.get("session_id") or "").strip() or None
        if not query:
            return ActionResult.failure(
                "Please tell me what you want me to search for.",
                data=self._empty_widget(query=query),
                request_id=request.request_id,
            )

        boundary_notice = "I'm checking online."
        started_at = time.monotonic()
        brave_status_code = 0
        brave_network_failed = False
        used_provider = ""

        brave_key = os.getenv("BRAVE_API_KEY", "").strip()
        response = None
        if brave_key:
            max_retries = 1
            for attempt in range(max_retries + 1):
                if time.monotonic() - started_at > SEARCH_HARD_TIMEOUT_SECONDS:
                    return ActionResult.failure(
                        f"{boundary_notice} Search timed out. Please try again.",
                        data=self._empty_widget(query=query),
                        request_id=request.request_id,
                    )
                try:
                    response = self.network.request(
                        capability_id=request.capability_id,
                        method="GET",
                        url=BRAVE_SEARCH_URL,
                        params={"q": query, "count": 5},
                        headers={"Accept": "application/json", "X-Subscription-Token": brave_key},
                        as_json=True,
                        timeout=5,
                        request_id=request.request_id,
                        session_id=session_id,
                    )
                    brave_status_code = int(response.get("status_code") or 0)
                    if brave_status_code == 200:
                        used_provider = "brave"
                        break
                    response = None
                    break
                except Exception as error:
                    if error.__class__.__name__ != "NetworkMediatorError":
                        raise
                    logger.debug("Attempt %s failed: %s", attempt + 1, error)
                    if attempt == max_retries:
                        brave_network_failed = True
                        response = None
                        break
                    time.sleep(0.5)
                    continue

        if response is None:
            if brave_network_failed:
                return ActionResult.failure(
                    f"{boundary_notice} I couldn't complete the search due to a network issue. Try again shortly or use a narrower query.",
                    data=self._empty_widget(query=query),
                    request_id=request.request_id,
                )
            if time.monotonic() - started_at > SEARCH_HARD_TIMEOUT_SECONDS:
                return ActionResult.failure(
                    f"{boundary_notice} Search timed out. Please try again.",
                    data=self._empty_widget(query=query),
                    request_id=request.request_id,
                )
            response = self._search_duckduckgo(request, query, session_id)
            if response and int(response.get("status_code") or 0) == 200:
                used_provider = "duckduckgo"
            else:
                if brave_status_code == 401:
                    return ActionResult.failure(
                        f"{boundary_notice} Search authentication failed. Check the configured search provider credentials.",
                        data=self._empty_widget(query=query),
                        request_id=request.request_id,
                    )
                if brave_status_code == 429:
                    return ActionResult.failure(
                        f"{boundary_notice} Search rate limit reached. Please try again in a moment.",
                        data=self._empty_widget(query=query),
                        request_id=request.request_id,
                    )
                if brave_status_code == 202:
                    return ActionResult.failure(
                        f"{boundary_notice} Search is temporarily unavailable. Please try again later.",
                        data=self._empty_widget(query=query),
                        request_id=request.request_id,
                    )
                return ActionResult.failure(
                    f"{boundary_notice} I couldn't complete the search due to a network issue. Try again shortly or use a narrower query.",
                    data=self._empty_widget(query=query),
                    request_id=request.request_id,
                )

        status_code = int(response.get("status_code") or 0)
        data = response.get("data") or {}
        if status_code != 200:
            return ActionResult.failure(
                f"{boundary_notice} I received an unexpected response from the search service.",
                data=self._empty_widget(query=query),
                request_id=request.request_id,
            )

        results = self._parse_results(data)[:5]
        if not results:
            return ActionResult.ok(
                message=(
                    f"{boundary_notice} I couldn't find solid results for \"{query}\".\n"
                    "Try a more specific query, a company/site name, or a shorter topic phrase."
                ),
                data=self._empty_widget(query=query, provider=used_provider),
                request_id=request.request_id,
            )

        top_domains = []
        for result in results[:3]:
            domain = self._extract_domain(result.get("url", ""))
            if domain and domain not in top_domains:
                top_domains.append(domain)

        elapsed_seconds = time.monotonic() - started_at
        avg_latency = self._record_latency(elapsed_seconds)
        logger.info("web_search latency=%.2fs avg=%.2fs query=%s", elapsed_seconds, avg_latency, query[:80])

        findings_block = ResponseTemplates.top_findings_block([result["title"] for result in results[:3]])
        sources_block = ResponseTemplates.sources_block(top_domains)
        provider_label = self._format_provider_label(used_provider)
        confidence_label = "Medium" if used_provider == "brave" else "Medium-Low"
        source_packets = self._collect_source_packets(
            capability_id=request.capability_id,
            results=results,
            request_id=request.request_id,
            session_id=session_id,
        )
        researched_summary = self._synthesize_researched_summary(
            query=query,
            results=results,
            source_packets=source_packets,
            request_id=request.request_id,
            session_id=session_id,
        )

        report_sections = [
            "Answer",
            f"{boundary_notice} {researched_summary}",
            "",
            findings_block.replace("Top Findings", "Key Points"),
            "",
            sources_block,
            "",
            f"Provider: {provider_label}",
            f"Source pages reviewed: {len(source_packets)}",
            "",
            "Confidence",
            confidence_label,
            "",
            f"Search latency: {elapsed_seconds:.1f}s (avg {avg_latency:.1f}s).",
            "Open any dashboard result for full article detail.",
            "",
            "Try next",
            "- summarize these search results",
            "- compare the top 3 search results",
            "- which result is the most reliable source and why",
        ]
        user_message = "\n".join(report_sections)

        return ActionResult.ok(
            message=user_message,
            data=self._search_widget(
                query=query,
                provider=used_provider,
                latency_seconds=elapsed_seconds,
                results=results,
                researched_summary=researched_summary,
                source_pages_read=len(source_packets),
            ),
            request_id=request.request_id,
        )
