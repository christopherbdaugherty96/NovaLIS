from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from src.actions.action_result import ActionResult

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STORY_DIR = PROJECT_ROOT / "nova_workspace" / "story_tracker"
TRACKED_TOPICS_PATH = STORY_DIR / "tracked_topics.json"
STORY_GRAPH_PATH = STORY_DIR / "story_graph.json"
MAX_EVENTS_PER_UPDATE = 6
RETENTION_DAYS = 30


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(topic: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", (topic or "").lower()).strip("_")
    return cleaned or "untitled"


def _story_path(topic: str) -> Path:
    return STORY_DIR / f"story_{_slug(topic)}.json"


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def _snapshot_hash(snapshot: dict[str, Any]) -> str:
    raw = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]


class StoryTrackerExecutor:
    def _tokenize(self, text: str) -> set[str]:
        return {w for w in re.findall(r"[a-zA-Z]{4,}", (text or "").lower())}

    def _story_keywords(self, snapshots: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for snap in snapshots:
            for event in snap.get("events", []):
                headline = event.get("headline", "")
                for token in self._tokenize(headline):
                    counts[token] = counts.get(token, 0) + 1
        return counts

    def _tracked_topics(self) -> list[str]:
        payload = _read_json(TRACKED_TOPICS_PATH, {"topics": []})
        topics = payload.get("topics", []) if isinstance(payload, dict) else []
        return [str(t).strip() for t in topics if str(t).strip()]

    def _save_tracked_topics(self, topics: list[str]) -> None:
        dedup: list[str] = []
        for t in topics:
            if t not in dedup:
                dedup.append(t)
        _write_json(TRACKED_TOPICS_PATH, {"topics": dedup, "updated_at": _utc_now()})

    def _load_graph(self) -> dict[str, Any]:
        payload = _read_json(STORY_GRAPH_PATH, {"links": []})
        if not isinstance(payload, dict):
            return {"links": []}
        payload.setdefault("links", [])
        return payload

    def _save_graph(self, graph: dict[str, Any]) -> None:
        _write_json(STORY_GRAPH_PATH, graph)

    def _prune_snapshots(self, snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
        kept: list[dict[str, Any]] = []
        for snap in snapshots:
            ts = str(snap.get("timestamp_utc", "")).strip()
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                dt = None
            if dt is None or dt >= cutoff:
                kept.append(snap)
        return kept

    def _load_story(self, topic: str) -> dict[str, Any]:
        path = _story_path(topic)
        default = {
            "story_id": f"story_{_slug(topic)}",
            "topic": topic,
            "created_at": _utc_now(),
            "snapshots": [],
        }
        payload = _read_json(path, default)
        if not isinstance(payload, dict):
            return default
        payload.setdefault("story_id", f"story_{_slug(topic)}")
        payload.setdefault("topic", topic)
        payload.setdefault("created_at", _utc_now())
        payload.setdefault("snapshots", [])
        return payload

    def _save_story(self, story: dict[str, Any]) -> None:
        topic = story.get("topic", "untitled")
        story["snapshots"] = self._prune_snapshots(story.get("snapshots", []))
        _write_json(_story_path(topic), story)

    def _extract_events(self, topic: str, headlines: list[dict[str, str]]) -> list[dict[str, Any]]:
        topic_terms = [t for t in re.findall(r"[a-zA-Z0-9]+", topic.lower()) if len(t) >= 3]
        selected: list[dict[str, str]] = []
        for item in headlines:
            title = (item.get("title") or "").strip()
            if not title:
                continue
            lower = title.lower()
            if topic_terms and any(term in lower for term in topic_terms):
                selected.append(item)
        if not selected:
            selected = headlines[:3]

        events: list[dict[str, Any]] = []
        today = datetime.now(timezone.utc).date().isoformat()
        for item in selected[:MAX_EVENTS_PER_UPDATE]:
            title = (item.get("title") or "").strip()
            if not title:
                continue
            tags = [term for term in topic_terms if term in title.lower()][:4]
            events.append(
                {
                    "date": today,
                    "source": (item.get("source") or "Unknown").strip(),
                    "headline": title,
                    "summary": title,
                    "confidence": "medium",
                    "tags": tags,
                    "url": (item.get("url") or "").strip(),
                }
            )
        return events

    def _new_snapshot(self, topic: str, events: list[dict[str, Any]]) -> dict[str, Any]:
        open_questions = [f"What confirmed next step is visible for {topic}?"]
        signals = ["Follow-up reporting from primary sources", "Official statements or filings"]
        snapshot = {
            "timestamp_utc": _utc_now(),
            "events": events,
            "open_questions": open_questions,
            "signals_to_watch": signals,
        }
        snapshot["version_hash"] = _snapshot_hash(snapshot)
        return snapshot

    def _render_story(self, story: dict[str, Any], snapshot: dict[str, Any] | None) -> str:
        topic = story.get("topic", "Unknown topic")
        if not snapshot:
            return (
                f"STORY TRACKER - {topic}\n\n"
                "No update performed since last snapshot.\n"
                f'Use "update story {topic}" to refresh.'
            )

        lines = [f"STORY TRACKER - {topic}", ""]
        lines.append(f"Snapshots stored: {len(story.get('snapshots', []))}")
        lines.append(f"Latest update: {snapshot.get('timestamp_utc', 'unknown')}")
        lines.append("")
        lines.append("Timeline")
        for event in snapshot.get("events", []):
            lines.append(f"- {event.get('date', '')}: {event.get('headline', '')} ({event.get('source', 'Unknown')})")
        lines.append("")
        lines.append("Open Questions")
        for q in snapshot.get("open_questions", []):
            lines.append(f"- {q}")
        lines.append("")
        lines.append("Signals to Watch")
        for s in snapshot.get("signals_to_watch", []):
            lines.append(f"- {s}")
        lines.append("")
        lines.append(f"Snapshot Hash: {snapshot.get('version_hash', 'unknown')}")
        lines.append("Try next:")
        lines.append(f"- update story {topic}")
        lines.append(f"- compare story {topic}")
        lines.append(f"- stop tracking story {topic}")
        return "\n".join(lines)

    def execute_update(self, request) -> ActionResult:
        params = request.params or {}
        action = (params.get("action") or "update").strip().lower()
        headlines = params.get("headlines") or []
        headlines = headlines if isinstance(headlines, list) else []

        if action in {"update_all", "brief_with_tracking"}:
            topics = self._tracked_topics()
            if not topics:
                return ActionResult.failure("No tracked stories found. Use 'track story <topic>' first.", request_id=request.request_id)
            updated: list[dict[str, str]] = []
            for topic in topics:
                story = self._load_story(topic)
                events = self._extract_events(topic, headlines)
                snap = self._new_snapshot(topic, events)
                story["snapshots"].append(snap)
                self._save_story(story)
                updated.append({"topic": topic, "hash": snap["version_hash"]})
            msg = "Updated tracked stories:\n" + "\n".join(f"- {u['topic']} ({u['hash']})" for u in updated)
            return ActionResult.ok(
                message=f"{msg}\n\nTry next: show story <topic> or compare two stories.",
                data={"widget": {"type": "story_tracker_update", "data": {"updated": updated}}},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )

        topic = (params.get("topic") or "").strip()
        if action == "link":
            raw_topics = params.get("topics") or []
            if not isinstance(raw_topics, list) or len(raw_topics) != 2:
                return ActionResult.failure("Provide two topics to link.", request_id=request.request_id)
            left = str(raw_topics[0]).strip()
            right = str(raw_topics[1]).strip()
            if not left or not right or left.lower() == right.lower():
                return ActionResult.failure("Provide two distinct topics to link.", request_id=request.request_id)

            graph = self._load_graph()
            links = graph.get("links", [])
            key = tuple(sorted([left.lower(), right.lower()]))
            existing = {
                tuple(sorted([str(item.get("from", "")).lower(), str(item.get("to", "")).lower()]))
                for item in links
                if isinstance(item, dict)
            }
            if key not in existing:
                links.append({"from": left, "to": right, "type": "user_linked", "created_at_utc": _utc_now()})
            graph["links"] = links
            graph["updated_at_utc"] = _utc_now()
            self._save_graph(graph)

            return ActionResult.ok(
                message=(
                    f"Linked story '{left}' to '{right}'.\n\n"
                    "Try next:\n"
                    "- show relationship graph\n"
                    f"- compare stories {left} and {right}"
                ),
                data={"widget": {"type": "story_tracker_update", "data": {"action": "link", "topics": [left, right]}}},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )

        if not topic:
            return ActionResult.failure("No story topic provided.", request_id=request.request_id)

        topics = self._tracked_topics()
        if action == "track":
            if topic not in topics:
                topics.append(topic)
                self._save_tracked_topics(topics)
            story = self._load_story(topic)
            if not story.get("snapshots"):
                events = self._extract_events(topic, headlines)
                snap = self._new_snapshot(topic, events)
                story["snapshots"].append(snap)
                self._save_story(story)
                return ActionResult.ok(
                    message=(
                        f"Started tracking story '{topic}'.\n"
                        f"Snapshot hash: {snap['version_hash']}.\n"
                        f"Events captured: {len(events)}.\n\n"
                        f"Try next:\n- update story {topic}\n- show story {topic}"
                    ),
                    data={"widget": {"type": "story_tracker_update", "data": {"topic": topic, "hash": snap["version_hash"]}}},
                    request_id=request.request_id,
                    authority_class="read_only",
                    external_effect=False,
                    reversible=True,
                )
            self._save_story(story)
            latest = story["snapshots"][-1]
            return ActionResult.ok(
                message=(
                    f"Story '{topic}' is already tracked.\n"
                    f"Latest snapshot hash: {latest.get('version_hash', 'unknown')}.\n\n"
                    f"Try next:\n- update story {topic}\n- show story {topic}"
                ),
                data={"widget": {"type": "story_tracker_update", "data": {"topic": topic}}},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )

        if action == "stop":
            kept = [t for t in topics if t.lower() != topic.lower()]
            self._save_tracked_topics(kept)
            return ActionResult.ok(
                message=f"Stopped tracking story '{topic}'. You can track it again later with: track story {topic}",
                data={"widget": {"type": "story_tracker_update", "data": {"topic": topic, "stopped": True}}},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )

        story = self._load_story(topic)
        events = self._extract_events(topic, headlines)
        snapshot = self._new_snapshot(topic, events)
        story["snapshots"].append(snapshot)
        self._save_story(story)
        if topic not in topics:
            topics.append(topic)
            self._save_tracked_topics(topics)

        return ActionResult.ok(
            message=(
                f"Updated story '{topic}'.\n"
                f"Snapshot hash: {snapshot['version_hash']}.\n"
                f"Events captured: {len(events)}.\n\n"
                f"Try next:\n- show story {topic}\n- compare story {topic}"
            ),
            data={"widget": {"type": "story_tracker_update", "data": {"topic": topic, "hash": snapshot["version_hash"]}}},
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def execute_view(self, request) -> ActionResult:
        params = request.params or {}
        action = (params.get("action") or "show").strip().lower()

        if action == "show_graph":
            graph = self._load_graph()
            links = [item for item in graph.get("links", []) if isinstance(item, dict)]
            if not links:
                return ActionResult.ok(
                    message="RELATIONSHIP GRAPH\n\nNo story links defined yet.\nUse: link story <A> to <B>",
                    data={"widget": {"type": "story_tracker_view", "data": {"action": "show_graph", "links": []}}},
                    request_id=request.request_id,
                    authority_class="read_only",
                    external_effect=False,
                    reversible=True,
                )

            lines = ["RELATIONSHIP GRAPH", ""]
            for link in links:
                left = str(link.get("from", "")).strip()
                right = str(link.get("to", "")).strip()
                if not left or not right:
                    continue
                lines.append(f"{left}")
                lines.append(f"  -> linked to {right}")
            return ActionResult.ok(
                message="\n".join(lines + ["", "Try next: compare two linked stories or update a story."]),
                data={"widget": {"type": "story_tracker_view", "data": {"action": "show_graph", "links": links}}},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )

        if action == "compare_stories":
            topics = params.get("topics") or []
            if not isinstance(topics, list) or len(topics) != 2:
                return ActionResult.failure("Provide exactly two story topics to compare.", request_id=request.request_id)
            left_topic = str(topics[0]).strip()
            right_topic = str(topics[1]).strip()
            if not left_topic or not right_topic:
                return ActionResult.failure("Provide exactly two story topics to compare.", request_id=request.request_id)

            left_story = self._load_story(left_topic)
            right_story = self._load_story(right_topic)
            left_snaps = left_story.get("snapshots", [])
            right_snaps = right_story.get("snapshots", [])
            if not left_snaps or not right_snaps:
                return ActionResult.failure(
                    "One or both stories have no snapshots yet. Update each story first.",
                    request_id=request.request_id,
                )

            left_kw = self._story_keywords(left_snaps)
            right_kw = self._story_keywords(right_snaps)
            overlap = sorted(set(left_kw.keys()) & set(right_kw.keys()))

            overlap_ranked = sorted(
                overlap,
                key=lambda key: (left_kw.get(key, 0) + right_kw.get(key, 0)),
                reverse=True,
            )[:8]

            lines = [
                f"CROSS-STORY COMPARISON - {left_topic} vs {right_topic}",
                "",
                f"{left_topic}: {len(left_snaps)} snapshots",
                f"{right_topic}: {len(right_snaps)} snapshots",
                "",
                "Shared Signals",
            ]
            if overlap_ranked:
                for term in overlap_ranked:
                    score = left_kw.get(term, 0) + right_kw.get(term, 0)
                    lines.append(f"- {term} ({score})")
            else:
                lines.append("- No significant shared signals detected in current snapshots.")

            lines.extend(
                [
                    "",
                    "Note: This is an invocation-bound comparison of stored snapshots, not predictive analysis.",
                    "",
                    f"Try next: show story {left_topic} or show story {right_topic}.",
                ]
            )

            return ActionResult.ok(
                message="\n".join(lines),
                data={
                    "widget": {
                        "type": "story_tracker_view",
                        "data": {
                            "action": "compare_stories",
                            "topics": [left_topic, right_topic],
                            "shared_terms": overlap_ranked,
                        },
                    }
                },
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )

        topic = (params.get("topic") or "").strip()
        if not topic:
            return ActionResult.failure("No story topic provided.", request_id=request.request_id)

        story = self._load_story(topic)
        snapshots = story.get("snapshots", [])
        if not snapshots:
            return ActionResult.failure(
                f"No update performed since last snapshot.\nUse \"update story {topic}\" to refresh.",
                request_id=request.request_id,
            )

        if action == "compare":
            days = int(params.get("days") or 7)
            cutoff = datetime.now(timezone.utc) - timedelta(days=max(1, min(days, 365)))
            subset: list[dict[str, Any]] = []
            for snap in snapshots:
                ts = snap.get("timestamp_utc", "")
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except Exception:
                    dt = None
                if dt is not None and dt >= cutoff:
                    subset.append(snap)
            if not subset:
                return ActionResult.ok(
                    message=f"No snapshots for '{topic}' in the last {days} days.",
                    data={"widget": {"type": "story_tracker_view", "data": {"topic": topic, "days": days, "count": 0}}},
                    request_id=request.request_id,
                    authority_class="read_only",
                    external_effect=False,
                    reversible=True,
                )
            latest = subset[-1]
            earlier = subset[0]
            msg = (
                f"STORY COMPARISON - {topic} (last {days} days)\n\n"
                f"Snapshots considered: {len(subset)}\n"
                f"Earliest hash: {earlier.get('version_hash', 'unknown')}\n"
                f"Latest hash: {latest.get('version_hash', 'unknown')}\n"
                f"Latest event count: {len(latest.get('events', []))}\n\n"
                f"Try next:\n- show story {topic}\n- update story {topic}"
            )
            return ActionResult.ok(
                message=msg,
                data={"widget": {"type": "story_tracker_view", "data": {"topic": topic, "days": days, "count": len(subset)}}},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )

        latest = snapshots[-1]
        return ActionResult.ok(
            message=self._render_story(story, latest),
            data={"widget": {"type": "story_tracker_view", "data": {"topic": topic, "hash": latest.get("version_hash", "")}}},
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )
