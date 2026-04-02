from __future__ import annotations

from fastapi.testclient import TestClient

from src import brain_server
from src.api import live_screen_api


class _FakeOCR:
    def extract_text(self, image_path: str) -> str:
        assert image_path
        return "Pricing calculator Booking CTA Contact"


class _FakeVision:
    def analyze(self, **kwargs) -> dict:
        assert kwargs["user_query"] == "explain this page"
        return {
            "summary": "This looks like a landing page with pricing, booking, and contact actions.",
            "next_steps": ["Review the pricing section.", "Check the booking CTA copy."],
            "page_kind": "landing_page",
            "what_matters": "The page is guiding the visitor toward booking.",
            "key_actions": ["book now", "contact"],
            "follow_up_prompts": ["what matters most here", "what should i click next"],
            "signals": {"page_title": "Shared browser tab"},
        }


def test_live_screen_api_analyzes_uploaded_frame(monkeypatch):
    monkeypatch.setattr(live_screen_api, "ocr_pipeline", _FakeOCR())
    monkeypatch.setattr(live_screen_api, "vision_analyzer", _FakeVision())

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/live-screen/analyze",
        data={"query": "explain this page", "source_label": "Shared browser tab"},
        files={"image": ("frame.png", b"fake-image-bytes", "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis_available"] is True
    assert payload["summary"].startswith("This looks like a landing page")
    assert payload["next_steps"] == ["Review the pricing section.", "Check the booking CTA copy."]
    assert payload["page_kind"] == "landing_page"
    assert payload["what_matters"] == "The page is guiding the visitor toward booking."
    assert payload["key_actions"] == ["book now", "contact"]
    assert payload["follow_up_prompts"] == ["what matters most here", "what should i click next"]
    assert payload["source_label"] == "Shared browser tab"


def test_live_screen_api_requires_frame_upload():
    client = TestClient(brain_server.app)
    response = client.post(
        "/api/live-screen/analyze",
        data={"query": "explain this page", "source_label": "Shared browser tab"},
        files={"image": ("frame.png", b"", "image/png")},
    )

    assert response.status_code == 400
    assert "shared screen frame is required" in response.json()["detail"].lower()
