from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def deterministic_simulation_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    monkeypatch.setenv("WEATHER_API_KEY", "test-weather-key")

    def fake_network_request(
        self,
        *,
        capability_id=None,
        method=None,
        url=None,
        json_payload=None,
        params=None,
        headers=None,
        as_json=True,
        timeout=5,
        request_id=None,
        session_id=None,
    ):
        del self, capability_id, method, json_payload, headers, timeout, request_id, session_id
        lower_url = str(url or "").lower()

        if "visualcrossing" in lower_url:
            return {
                "status_code": 200,
                "data": {
                    "resolvedAddress": "Ann Arbor, MI",
                    "currentConditions": {"temp": 52.3, "conditions": "Clear"},
                    "days": [
                        {"tempmax": 56, "tempmin": 44, "conditions": "Clear"},
                        {"tempmax": 58, "tempmin": 45, "conditions": "Partly cloudy"},
                    ],
                    "alerts": [],
                },
            }

        if not as_json:
            if any(
                marker in lower_url
                for marker in (
                    "rss",
                    "feed",
                    "newshour/feeds",
                    "abcnews/topstories",
                    "index.xml",
                    "techcrunch.com/feed",
                    ".xml",
                )
            ):
                return {
                    "status_code": 200,
                    "text": (
                        "<?xml version='1.0' encoding='UTF-8'?>"
                        "<rss><channel>"
                        "<item>"
                        "<title>AI hardware race accelerates globally</title>"
                        "<link>https://abcnews.go.com/story-ai-hardware</link>"
                        "<description>Chipmakers announce new accelerator roadmaps.</description>"
                        "<pubDate>Tue, 10 Mar 2026 10:00:00 GMT</pubDate>"
                        "</item>"
                        "<item>"
                        "<title>Energy policy update from regulators</title>"
                        "<link>https://www.reuters.com/story-energy-policy</link>"
                        "<description>Regulators discuss policy timelines and oversight.</description>"
                        "<pubDate>Tue, 10 Mar 2026 09:30:00 GMT</pubDate>"
                        "</item>"
                        "<item>"
                        "<title>Cybersecurity teams tighten system checks</title>"
                        "<link>https://www.foxnews.com/story-cyber-checks</link>"
                        "<description>Organizations expand diagnostics and resilience checks.</description>"
                        "<pubDate>Tue, 10 Mar 2026 09:00:00 GMT</pubDate>"
                        "</item>"
                        "</channel></rss>"
                    ),
                }

            return {
                "status_code": 200,
                "text": (
                    "<html><body>"
                    "<h1>AI hardware update</h1>"
                    "<p>Major vendors reported new accelerator launches and supply updates.</p>"
                    "<p>Analysts highlighted demand from enterprise and cloud workloads.</p>"
                    "</body></html>"
                ),
            }

        query = str((params or {}).get("q") or "").strip() or "test query"
        return {
            "status_code": 200,
            "data": {
                "web": {
                    "results": [
                        {
                            "title": f"{query} - Source A",
                            "url": "https://abcnews.go.com/story-a",
                            "description": f"Summary for {query} from Source A.",
                        },
                        {
                            "title": f"{query} - Source B",
                            "url": "https://www.foxnews.com/story-b",
                            "description": f"Summary for {query} from Source B.",
                        },
                        {
                            "title": f"{query} - Source C",
                            "url": "https://www.reuters.com/story-c",
                            "description": f"Summary for {query} from Source C.",
                        },
                    ]
                }
            },
        }

    def fake_generate_chat(*args, **kwargs):
        prompt = ""
        if args:
            prompt = str(args[0])
        if "Daily Intelligence Brief" in prompt:
            return (
                "Top Headlines\n"
                "1. AI regulation expands globally.\n"
                "Key Developments\n"
                "- Oversight frameworks are converging.\n"
                "Signals to Watch\n"
                "- Upcoming committee actions."
            )
        return "Summary\nClear synthetic analysis.\n\nKey Findings\n- Finding 1\n- Finding 2\n\nSources\n- abcnews.go.com"

    monkeypatch.setattr("src.governor.network_mediator.NetworkMediator.request", fake_network_request)
    monkeypatch.setattr("src.executors.multi_source_reporting_executor.generate_chat", fake_generate_chat)
    monkeypatch.setattr("src.skills.general_chat.generate_chat", fake_generate_chat)
    monkeypatch.setattr("src.llm.llm_gateway.generate_chat", fake_generate_chat)
