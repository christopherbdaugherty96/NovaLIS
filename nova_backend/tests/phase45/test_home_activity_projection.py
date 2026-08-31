from __future__ import annotations

import asyncio
import json

from src import brain_server


def _activity(
    title: str,
    *,
    detail: str = "",
    origin: str = "",
    kind: str = "system",
    event_type: str = "PATTERN_REVIEW_VIEWED",
    capability_name: str = "",
    capability_id: str = "",
    timestamp: str = "",
    request_id: str = "",
) -> dict[str, object]:
    return {
        "title": title,
        "detail": detail,
        "activity_origin": origin,
        "kind": kind,
        "event_type": event_type,
        "capability_name": capability_name,
        "capability_id": capability_id,
        "timestamp": timestamp,
        "request_id": request_id,
    }


def test_home_prioritizes_older_user_system_status_over_newer_background_hydration():
    projected = brain_server._project_home_recent_activity(
        [
            _activity(
                "Read completed",
                detail="weather snapshot",
                origin="background_read",
                kind="read",
                event_type="ACTION_COMPLETED",
                capability_name="weather_snapshot",
                timestamp="12:03",
            ),
            _activity(
                "Model readiness check",
                detail="Local model endpoint",
                event_type="MODEL_NETWORK_CALL",
                kind="model",
                timestamp="12:02",
            ),
            _activity(
                "Read completed",
                detail="os diagnostics",
                origin="user_action",
                kind="read",
                event_type="ACTION_COMPLETED",
                capability_name="os_diagnostics",
                timestamp="12:01",
            ),
        ]
    )

    assert [item["title"] for item in projected] == [
        "System status",
        "Read completed",
        "Model readiness check",
    ]
    assert projected[0]["detail"] == "Read completed"
    assert projected[0]["activity_origin"] == "user_action"


def test_home_preserves_newest_first_order_within_meaningful_user_activity():
    projected = brain_server._project_home_recent_activity(
        [
            _activity("Newer user action", origin="user_action", kind="action", timestamp="12:02"),
            _activity("Older user action", origin="user_action", kind="action", timestamp="12:01"),
            _activity("Hydration", origin="background_read", kind="read", timestamp="12:03"),
        ]
    )

    assert [item["title"] for item in projected[:2]] == [
        "Newer user action",
        "Older user action",
    ]


def test_home_collapses_duplicate_visible_read_cards_without_changing_read_semantics():
    read_item = _activity(
        "Read completed",
        detail="os diagnostics",
        origin="user_action",
        kind="read",
        event_type="ACTION_COMPLETED",
        capability_name="os_diagnostics",
    )
    read_item.update(
        {
            "outcome_state": "read_succeeded",
            "authority_class": "read_only_local",
            "external_effect": "no",
        }
    )

    projected = brain_server._project_home_recent_activity([read_item, dict(read_item)])

    assert len(projected) == 1
    assert projected[0]["title"] == "System status"
    assert projected[0]["detail"] == "Read completed"
    assert projected[0]["outcome_state"] == "read_succeeded"
    assert projected[0]["authority_class"] == "read_only_local"
    assert projected[0]["external_effect"] == "no"
    assert read_item["title"] == "Read completed"
    assert read_item["detail"] == "os diagnostics"


def test_home_deduplicates_after_prioritizing_user_read_over_newer_background_copy():
    background_copy = _activity(
        "Read completed",
        detail="os diagnostics",
        origin="background_read",
        kind="read",
        event_type="ACTION_COMPLETED",
        capability_name="os_diagnostics",
        timestamp="12:02",
    )
    user_read = _activity(
        "Read completed",
        detail="os diagnostics",
        origin="user_action",
        kind="read",
        event_type="ACTION_COMPLETED",
        capability_name="os_diagnostics",
        timestamp="12:01",
    )

    projected = brain_server._project_home_recent_activity([background_copy, user_read])

    assert len(projected) == 1
    assert projected[0]["title"] == "System status"
    assert projected[0]["activity_origin"] == "user_action"


def test_home_keeps_diagnostics_failure_qualifier_in_visible_title():
    projected = brain_server._project_home_recent_activity(
        [
            _activity(
                "Action needs attention",
                detail="os diagnostics",
                origin="user_action",
                kind="action",
                event_type="ACTION_COMPLETED",
                capability_name="os_diagnostics",
            )
        ]
    )

    assert projected[0]["title"] == "System status — Action needs attention"
    assert projected[0]["detail"] == "Action needs attention"


def test_home_keeps_unmatched_network_subevent_as_bounded_background_evidence():
    projected = brain_server._project_home_recent_activity(
        [
            _activity(
                "External request",
                detail="weather.example",
                kind="network",
                event_type="EXTERNAL_NETWORK_CALL",
                capability_id="55",
            ),
            _activity("Pattern Review Viewed", detail="Pattern review activity"),
        ]
    )

    assert [item["title"] for item in projected] == ["Pattern Review Viewed", "External request"]


def test_home_prefers_completed_user_action_over_raw_network_subevent():
    projected = brain_server._project_home_recent_activity(
        [
            _activity(
                "External request",
                detail="weather.example",
                kind="network",
                event_type="EXTERNAL_NETWORK_CALL",
                capability_id="55",
            ),
            _activity(
                "Read completed",
                detail="weather snapshot",
                origin="user_action",
                kind="read",
                event_type="ACTION_COMPLETED",
                capability_name="weather_snapshot",
                capability_id="55",
            ),
        ]
    )

    assert [item["title"] for item in projected] == ["Read completed", "External request"]


def test_home_never_reserves_a_slot_for_background_when_foreground_fills_view():
    foreground = [
        _activity(f"User activity {index}", origin="user_action", kind="action")
        for index in range(4)
    ]
    projected = brain_server._project_home_recent_activity(
        foreground + [_activity("Hydration", origin="background_read", kind="read")]
    )

    assert [item["title"] for item in projected] == [f"User activity {index}" for index in range(4)]


def test_workspace_home_build_runs_off_websocket_event_loop(monkeypatch):
    expected = {"type": "workspace_home", "recent_activity": []}
    calls: list[tuple[object, dict[str, object]]] = []

    async def _to_thread(function, **kwargs):
        calls.append((function, kwargs))
        return expected

    async def _ws_send(_ws, payload):
        assert payload is expected

    monkeypatch.setattr(brain_server.asyncio, "to_thread", _to_thread)
    monkeypatch.setattr(brain_server, "ws_send", _ws_send)
    session_state: dict[str, object] = {}
    project_threads = object()

    result = asyncio.run(
        brain_server.send_workspace_home_widget(object(), session_state, project_threads)
    )

    assert result is expected
    assert calls == [
        (
            brain_server._build_workspace_home_widget,
            {"session_state": session_state, "project_threads": project_threads},
        )
    ]
    assert session_state["last_workspace_home"] is expected


def test_home_keeps_background_only_history_useful_and_bounded():
    projected = brain_server._project_home_recent_activity(
        [
            _activity("Weather refreshed", origin="background_read", kind="read"),
            _activity("Calendar refreshed", origin="background_read", kind="read"),
            _activity("News refreshed", origin="background_read", kind="read"),
        ]
    )

    assert [item["title"] for item in projected] == [
        "Weather refreshed",
        "Calendar refreshed",
    ]


def test_home_projection_is_stable_for_persisted_receipt_shape():
    persisted = json.loads(
        json.dumps(
            [
                _activity(
                    "Read completed",
                    detail="os diagnostics",
                    origin="user_action",
                    kind="read",
                    event_type="ACTION_COMPLETED",
                    capability_name="os_diagnostics",
                ),
                _activity("Model readiness check", event_type="MODEL_NETWORK_CALL", kind="model"),
            ]
        )
    )

    projected = brain_server._project_home_recent_activity(persisted)

    assert [item["title"] for item in projected] == [
        "System status",
        "Model readiness check",
    ]


def test_home_reads_a_deeper_bounded_window_before_ranking_restart_hydration(monkeypatch):
    newer_hydration = [
        _activity(f"Hydration {index}", origin="background_read", kind="read")
        for index in range(20)
    ]
    persisted_user_read = _activity(
        "Read completed",
        detail="os diagnostics",
        origin="user_action",
        kind="read",
        event_type="ACTION_COMPLETED",
        capability_name="os_diagnostics",
    )
    requested_limits: list[tuple[int, int]] = []

    monkeypatch.setattr(
        brain_server.OSDiagnosticsExecutor,
        "_enabled_capability_entries",
        staticmethod(lambda: [{"id": 32, "name": "os_diagnostics"}]),
    )

    def _recent(_enabled, *, limit, scan_line_limit):
        requested_limits.append((limit, scan_line_limit))
        return newer_hydration + [persisted_user_read], "bounded"

    monkeypatch.setattr(
        brain_server.OSDiagnosticsExecutor,
        "_recent_runtime_activity",
        staticmethod(_recent),
    )

    source = brain_server._home_recent_activity_source(
        {"recent_runtime_activity": newer_hydration[:12]}
    )
    projected = brain_server._project_home_recent_activity(source)

    assert requested_limits == [(1024, 8000)]
    assert requested_limits[0][1] <= 10000
    assert projected[0]["title"] == "System status"


def test_home_projection_fails_safely_for_missing_or_malformed_activity_fields():
    projected = brain_server._project_home_recent_activity(
        [None, "corrupt", {}, {"detail": "missing title"}, {"title": "Safe event", "detail": 42}]
    )

    assert projected == [{"title": "Safe event", "detail": "42"}]
    assert brain_server._project_home_recent_activity({"items": "corrupt"}) == []
