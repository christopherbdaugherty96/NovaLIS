from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def deterministic_eval_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")

    def fake_network_request(self, *, capability_id=None, method=None, url=None, params=None, headers=None, as_json=True, timeout=5):
        query = str((params or {}).get("q") or "").strip() or "test query"
        return {
            "status_code": 200,
            "data": {
                "web": {
                    "results": [
                        {
                            "title": f"{query} - Reuters Coverage",
                            "url": "https://www.reuters.com/markets/example",
                            "description": f"Structured finding about {query}.",
                        },
                        {
                            "title": f"{query} - BBC Coverage",
                            "url": "https://www.bbc.com/news/example",
                            "description": f"Additional context about {query}.",
                        },
                        {
                            "title": f"{query} - ABC Coverage",
                            "url": "https://abcnews.go.com/example",
                            "description": f"Cross-check details for {query}.",
                        },
                    ]
                }
            },
        }

    def fake_generate_chat(*args, **kwargs):
        prompt = str(args[0]) if args else ""
        if "Daily Intelligence Brief" in prompt:
            return (
                "Top Headlines\n"
                "1. Regulatory action advances.\n"
                "Key Developments\n"
                "- Multi-region policy movement.\n"
                "Signals to Watch\n"
                "- Next committee hearings."
            )
        return (
            "Summary\n"
            "Governments are tightening AI oversight while implementation timelines differ.\n\n"
            "Key Findings\n"
            "- EU guidance now emphasizes risk-based obligations.\n"
            "- U.S. agencies continue framework coordination.\n\n"
            "Sources\n"
            "- reuters.com\n"
            "- bbc.com\n\n"
            "Confidence\n"
            "0.82"
        )

    monkeypatch.setattr("src.governor.network_mediator.NetworkMediator.request", fake_network_request)
    monkeypatch.setattr("src.executors.multi_source_reporting_executor.generate_chat", fake_generate_chat)
    monkeypatch.setattr("src.skills.general_chat.generate_chat", fake_generate_chat)
    monkeypatch.setattr("src.llm.llm_gateway.generate_chat", fake_generate_chat)

