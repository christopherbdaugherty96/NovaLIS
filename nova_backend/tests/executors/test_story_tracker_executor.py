from __future__ import annotations

from types import SimpleNamespace
from datetime import datetime, timedelta, timezone


def _req(capability_id: int, params: dict):
    return SimpleNamespace(capability_id=capability_id, params=params, request_id="story-req")


def test_track_update_view_compare_stop(monkeypatch, tmp_path):
    from src.executors import story_tracker_executor as mod

    monkeypatch.setattr(mod, "STORY_DIR", tmp_path / "story_tracker")
    monkeypatch.setattr(mod, "TRACKED_TOPICS_PATH", (tmp_path / "story_tracker" / "tracked_topics.json"))

    executor = mod.StoryTrackerExecutor()
    headlines = [
        {"title": "EU advances AI regulation framework", "source": "Reuters", "url": "https://example.com/a"},
        {"title": "US Senate hearing on AI safety", "source": "AP", "url": "https://example.com/b"},
    ]

    tracked = executor.execute_update(_req(52, {"action": "track", "topic": "AI regulation", "headlines": headlines}))
    assert tracked.success is True
    assert "Started tracking story" in tracked.message
    assert tracked.authority_class == "persistent_change"
    assert tracked.reversible is False

    updated = executor.execute_update(_req(52, {"action": "update", "topic": "AI regulation", "headlines": headlines}))
    assert updated.success is True
    assert "Updated story" in updated.message
    assert updated.authority_class == "persistent_change"
    assert updated.reversible is False

    shown = executor.execute_view(_req(53, {"action": "show", "topic": "AI regulation"}))
    assert shown.success is True
    assert "STORY TRACKER - AI regulation" in shown.message
    assert "Bottom line:" in shown.message
    assert "Snapshot Hash:" in shown.message

    compared = executor.execute_view(_req(53, {"action": "compare", "topic": "AI regulation", "days": 7}))
    assert compared.success is True
    assert "STORY COMPARISON - AI regulation" in compared.message

    stopped = executor.execute_update(_req(52, {"action": "stop", "topic": "AI regulation"}))
    assert stopped.success is True
    assert "Stopped tracking story" in stopped.message
    assert stopped.authority_class == "persistent_change"


def test_compare_stories(monkeypatch, tmp_path):
    from src.executors import story_tracker_executor as mod

    monkeypatch.setattr(mod, "STORY_DIR", tmp_path / "story_tracker")
    monkeypatch.setattr(mod, "TRACKED_TOPICS_PATH", (tmp_path / "story_tracker" / "tracked_topics.json"))

    executor = mod.StoryTrackerExecutor()
    ai_headlines = [
        {"title": "US updates AI export policy", "source": "Reuters", "url": "https://example.com/a1"},
        {"title": "AI regulation debate expands in senate", "source": "AP", "url": "https://example.com/a2"},
    ]
    semi_headlines = [
        {"title": "Semiconductor export policy tightened", "source": "Reuters", "url": "https://example.com/s1"},
        {"title": "Chip makers respond to export regulation", "source": "AP", "url": "https://example.com/s2"},
    ]

    executor.execute_update(_req(52, {"action": "track", "topic": "AI regulation", "headlines": ai_headlines}))
    executor.execute_update(
        _req(52, {"action": "track", "topic": "semiconductor export controls", "headlines": semi_headlines})
    )

    compared = executor.execute_view(
        _req(
            53,
            {
                "action": "compare_stories",
                "topics": ["AI regulation", "semiconductor export controls"],
            },
        )
    )
    assert compared.success is True
    assert "CROSS-STORY COMPARISON - AI regulation vs semiconductor export controls" in compared.message
    assert "Shared Signals" in compared.message


def test_retention_and_relationship_graph(monkeypatch, tmp_path):
    from src.executors import story_tracker_executor as mod

    monkeypatch.setattr(mod, "STORY_DIR", tmp_path / "story_tracker")
    monkeypatch.setattr(mod, "TRACKED_TOPICS_PATH", (tmp_path / "story_tracker" / "tracked_topics.json"))
    monkeypatch.setattr(mod, "STORY_GRAPH_PATH", (tmp_path / "story_tracker" / "story_graph.json"))
    monkeypatch.setattr(mod, "RETENTION_DAYS", 30)

    executor = mod.StoryTrackerExecutor()
    topic = "AI regulation"
    story_path = (tmp_path / "story_tracker" / "story_ai_regulation.json")
    old_ts = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    story_path.parent.mkdir(parents=True, exist_ok=True)
    story_path.write_text(
        """{
  "story_id": "story_ai_regulation",
  "topic": "AI regulation",
  "created_at": "2026-01-01T00:00:00+00:00",
  "snapshots": [
    {"timestamp_utc": "%s", "events": [], "open_questions": [], "signals_to_watch": [], "version_hash": "oldhash"}
  ]
}""" % old_ts,
        encoding="utf-8",
    )

    updated = executor.execute_update(
        _req(52, {"action": "update", "topic": topic, "headlines": [{"title": "AI regulation update", "source": "AP", "url": "u"}]})
    )
    assert updated.success is True

    loaded = mod._read_json(story_path, {})
    snapshots = loaded.get("snapshots", [])
    assert len(snapshots) == 1
    assert snapshots[0].get("version_hash") != "oldhash"

    linked = executor.execute_update(
        _req(52, {"action": "link", "topics": ["AI regulation", "semiconductor export controls"]})
    )
    assert linked.success is True

    graph = executor.execute_view(_req(53, {"action": "show_graph"}))
    assert graph.success is True
    assert "RELATIONSHIP GRAPH" in graph.message
    assert "AI regulation" in graph.message
