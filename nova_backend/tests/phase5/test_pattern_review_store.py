from pathlib import Path

import pytest

from src.patterns.pattern_review_store import PatternReviewStore


def test_pattern_review_requires_explicit_opt_in(tmp_path: Path):
    store = PatternReviewStore(tmp_path / "pattern_review.json")

    with pytest.raises(PermissionError):
        store.generate_review(thread_summaries=[], memory_insights={})


def test_pattern_review_generates_and_resolves_advisory_proposals(tmp_path: Path):
    store = PatternReviewStore(tmp_path / "pattern_review.json")
    store.set_opt_in(True)

    thread_summaries = [
        {
            "name": "Deployment Issue",
            "key": "deployment issue",
            "health_state": "blocked",
            "latest_blocker": "Container path resolution still fails in runtime import setup.",
            "latest_next_action": "",
        },
        {
            "name": "Build Container",
            "key": "build container",
            "health_state": "blocked",
            "latest_blocker": "Container image path differs from expected deployment path.",
            "latest_next_action": "Inspect Dockerfile path configuration.",
        },
    ]
    memory_insights = {
        "deployment issue": {"memory_count": 3, "latest_decision": ""},
        "build container": {"memory_count": 1, "latest_decision": "Pin image tag"},
    }

    snapshot = store.generate_review(
        thread_summaries=thread_summaries,
        memory_insights=memory_insights,
    )

    assert snapshot["opt_in_enabled"] is True
    assert snapshot["active_count"] >= 2
    titles = [item["title"] for item in snapshot["proposals"]]
    assert any("blocked without a recorded next step" in title.lower() for title in titles)
    assert any("recurring blocker theme" in title.lower() for title in titles)

    proposal_id = snapshot["proposals"][0]["id"]
    post_accept, accepted = store.accept_proposal(proposal_id)
    assert accepted["id"] == proposal_id
    assert post_accept["active_count"] == snapshot["active_count"] - 1
    assert any("accepted" in item["summary"].lower() for item in post_accept["recent_decisions"])


def test_pattern_review_opt_out_clears_active_queue(tmp_path: Path):
    store = PatternReviewStore(tmp_path / "pattern_review.json")
    store.set_opt_in(True)
    store.generate_review(
        thread_summaries=[
            {
                "name": "Deployment Issue",
                "key": "deployment issue",
                "health_state": "blocked",
                "latest_blocker": "Container path still fails.",
                "latest_next_action": "",
            }
        ],
        memory_insights={},
    )

    snapshot = store.set_opt_in(False)
    assert snapshot["opt_in_enabled"] is False
    assert snapshot["active_count"] == 0
