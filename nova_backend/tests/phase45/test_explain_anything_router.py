from __future__ import annotations

from src.perception.explain_anything import ExplainAnythingRouter


def test_explain_anything_router_prefers_file_route_when_file_selected():
    router = ExplainAnythingRouter()
    route = router.decide(
        params={"file_path": "C:/tmp/readme.md"},
        context_snapshot={
            "browser": {"is_browser": True},
            "cursor": {"screen_width": 1920, "screen_height": 1080},
        },
    )
    assert route.kind == "file"
    assert route.file_path.endswith("readme.md")


def test_explain_anything_router_uses_browser_route_when_browser_active():
    router = ExplainAnythingRouter()
    route = router.decide(
        params={},
        context_snapshot={"browser": {"is_browser": True}, "cursor": {"screen_width": 1920, "screen_height": 1080}},
    )
    assert route.kind == "webpage"


def test_explain_anything_router_uses_screen_route_with_cursor_region():
    router = ExplainAnythingRouter()
    route = router.decide(
        params={},
        context_snapshot={"browser": {"is_browser": False}, "cursor": {"screen_width": 1920, "screen_height": 1080}},
    )
    assert route.kind == "screen"
