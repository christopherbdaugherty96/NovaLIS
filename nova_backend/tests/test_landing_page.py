from __future__ import annotations

from fastapi.testclient import TestClient

from src import brain_server


def test_landing_page_route_returns_product_preview():
    client = TestClient(brain_server.app)

    response = client.get("/landing")

    assert response.status_code == 200
    assert "Local-first AI, under your control." in response.text
    assert "Nova is a governed workspace assistant" in response.text
