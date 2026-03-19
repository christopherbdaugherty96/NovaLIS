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


def test_explain_anything_router_uses_working_context_file_for_followup_guidance():
    router = ExplainAnythingRouter()
    route = router.decide(
        params={
            "query": "help me do this",
            "followup": True,
            "working_context": {
                "task_type": "code_analysis",
                "selected_file": "C:/Nova-Project/nova_backend/src/brain_server.py",
            },
        },
        context_snapshot={"browser": {"is_browser": False}, "cursor": {"screen_width": 0, "screen_height": 0}},
    )
    assert route.kind == "file"
    assert route.reason in {"working_context_file", "followup_file", "file_selected"}
    assert route.file_path.endswith("brain_server.py")


def test_explain_anything_router_falls_back_to_working_context_file_when_no_screen_context():
    router = ExplainAnythingRouter()
    route = router.decide(
        params={"working_context": {"selected_file": "C:/tmp/notes.md"}},
        context_snapshot={"browser": {"is_browser": False}, "cursor": {"screen_width": 0, "screen_height": 0}},
    )
    assert route.kind == "file"
    assert route.reason in {"fallback_file_context", "file_selected"}


def test_explain_anything_router_uses_screen_route_for_explicit_screen_query_without_snapshot():
    router = ExplainAnythingRouter()
    route = router.decide(
        params={"query": "what am i looking at"},
        context_snapshot={"browser": {"is_browser": False}, "cursor": {"screen_width": 0, "screen_height": 0}},
    )
    assert route.kind == "screen"
    assert route.reason == "explicit_screen_query"
