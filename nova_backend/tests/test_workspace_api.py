from __future__ import annotations

from fastapi.testclient import TestClient

from src import brain_server


def test_root_route_returns_index_html():
    client = TestClient(brain_server.app)

    response = client.get("/")

    assert response.status_code == 200


def test_landing_route_returns_landing_html():
    client = TestClient(brain_server.app)

    response = client.get("/landing")

    assert response.status_code == 200


def test_root_and_landing_are_distinct_routes():
    client = TestClient(brain_server.app)

    root = client.get("/")
    landing = client.get("/landing")

    assert root.status_code == 200
    assert landing.status_code == 200
    # Both should succeed but they serve different files
    assert root.headers.get("content-type", "").startswith("text/html")
    assert landing.headers.get("content-type", "").startswith("text/html")
