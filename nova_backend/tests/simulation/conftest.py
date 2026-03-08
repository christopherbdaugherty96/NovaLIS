from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def deterministic_simulation_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")

    def fake_network_request(self, *, capability_id=None, method=None, url=None, params=None, headers=None, as_json=True, timeout=5):
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
