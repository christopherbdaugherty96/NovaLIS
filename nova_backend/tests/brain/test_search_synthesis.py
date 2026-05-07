from src.brain.search_synthesis import (
    EvidenceConfidence,
    render_evidence_notes,
    synthesize_search_evidence,
)


def test_search_synthesis_builds_source_backed_evidence_from_packets():
    evidence = synthesize_search_evidence(
        query="latest AI model releases",
        results=[
            {
                "title": "Model launch roundup",
                "url": "https://reuters.com/technology/models",
                "snippet": "Several AI labs announced new models.",
            },
            {
                "title": "AI release notes",
                "url": "https://apnews.com/article/releases",
                "snippet": "New reasoning and coding models shipped.",
            },
        ],
        source_packets=[
            {
                "title": "Model launch roundup",
                "url": "https://reuters.com/technology/models",
                "text": "Lab A announced a new reasoning model this week. Details may change.",
            },
            {
                "title": "AI release notes",
                "url": "https://apnews.com/article/releases",
                "text": "Lab B released a coding model for developers.",
            },
        ],
    )

    assert evidence.evidence_status == "source_backed"
    assert evidence.confidence == EvidenceConfidence.HIGH
    assert evidence.source_pages_read == 2
    assert evidence.result_count == 2
    assert evidence.source_urls == ["https://reuters.com/technology/models", "https://apnews.com/article/releases"]
    assert evidence.claims[0].source_url == "https://reuters.com/technology/models"
    assert "announced a new reasoning model" in evidence.claims[0].claim
    assert "Nova reviewed 2 source pages" in " ".join(evidence.known)


def test_search_synthesis_falls_back_to_snippet_backed_evidence():
    evidence = synthesize_search_evidence(
        query="recent EV sales",
        results=[
            {
                "title": "EV sales update",
                "url": "https://example.com/ev",
                "snippet": "EV sales grew in some regions and slowed in others.",
            }
        ],
        source_packets=[],
    )

    assert evidence.evidence_status == "snippet_backed"
    assert evidence.confidence == EvidenceConfidence.MEDIUM
    assert evidence.claims[0].confidence == EvidenceConfidence.LOW
    assert "Only search result title/snippet was available" in evidence.claims[0].uncertainty
    assert any("not readable" in item for item in evidence.unclear)


def test_search_synthesis_low_relevance_reports_weak_or_no_evidence():
    evidence = synthesize_search_evidence(
        query="Zorblax Quantum Sandwich Labs",
        results=[
            {"title": "Quantum computing news", "url": "https://example.com/q", "snippet": "General quantum news."}
        ],
        low_relevance=True,
    )

    assert evidence.evidence_status == "weak_or_no_evidence"
    assert evidence.confidence == EvidenceConfidence.LOW
    assert evidence.claims == []
    assert "little reliable evidence" in evidence.unclear[0]


def test_search_synthesis_downgrades_weak_query_match():
    evidence = synthesize_search_evidence(
        query="qzxqzxqzx nonexistent topic with 1000 sources",
        results=[
            {
                "title": "Kafka topic configuration guide",
                "url": "https://example.com/kafka",
                "snippet": "A general guide to configuring message broker topics and source connectors.",
            },
            {
                "title": "Database source connector reference",
                "url": "https://example.com/connectors",
                "snippet": "Documentation for source connector setup and events.",
            },
        ],
        source_packets=[
            {
                "title": "Kafka topic configuration guide",
                "url": "https://example.com/kafka",
                "text": "This page explains message broker topic settings.",
            },
            {
                "title": "Database source connector reference",
                "url": "https://example.com/connectors",
                "text": "This reference covers connector setup.",
            },
        ],
    )

    assert evidence.confidence == EvidenceConfidence.LOW
    assert evidence.evidence_status == "source_backed"
    assert all(claim.confidence == EvidenceConfidence.LOW for claim in evidence.claims)
    assert all("weak or unrelated" in claim.uncertainty for claim in evidence.claims)
    assert any("weak or unrelated" in item for item in evidence.unclear)


def test_search_evidence_serializes_to_plain_dict():
    evidence = synthesize_search_evidence(
        query="coffee alzheimer evidence",
        results=[
            {
                "title": "Coffee and health",
                "url": "https://example.com/coffee",
                "snippet": "Studies are mixed and do not prove prevention.",
            }
        ],
    )

    payload = evidence.to_dict()

    assert payload["query"] == "coffee alzheimer evidence"
    assert payload["confidence"] == "medium"
    assert payload["claims"][0]["source_url"] == "https://example.com/coffee"
    assert payload["source_urls"] == ["https://example.com/coffee"]
    assert payload["provider_status"] == "ok"
    assert payload["freshness_status"] == "unknown"
    assert payload["source_credibility"][0]["credibility"] == "unknown"


def test_render_evidence_notes_returns_user_facing_lines():
    evidence = synthesize_search_evidence(
        query="current AI regulation",
        results=[
            {"title": "AI regulation", "url": "https://example.com/reg", "snippet": "Regulators proposed rules."}
        ],
    )

    confidence, known, unclear = render_evidence_notes(evidence)

    assert confidence == "Medium"
    assert "Governed search returned 1 result" in known
    assert "Current facts may change" in unclear


def test_search_synthesis_marks_stale_sources_low_confidence():
    evidence = synthesize_search_evidence(
        query="current port strike status",
        results=[
            {
                "title": "Port strike report",
                "url": "https://reuters.com/world/port-strike",
                "snippet": "Port workers remained on strike.",
                "published": "2025-01-01T12:00:00Z",
            }
        ],
        source_packets=[
            {
                "title": "Port strike report",
                "url": "https://reuters.com/world/port-strike",
                "text": "Port workers remained on strike during negotiations.",
                "published": "2025-01-01T12:00:00Z",
            }
        ],
        reference_date="2026-05-07T00:00:00Z",
        stale_after_days=30,
    )

    assert evidence.freshness_status == "stale"
    assert evidence.confidence == EvidenceConfidence.LOW
    assert any("stale" in item for item in evidence.unclear)


def test_search_synthesis_downgrades_unknown_and_fake_source_signals():
    evidence = synthesize_search_evidence(
        query="verified supply chain report",
        results=[
            {
                "title": "Supply chain rumor",
                "url": "https://fake-example-news.test/supply-chain",
                "snippet": "A viral post claims the supply chain changed overnight.",
            },
            {
                "title": "Unverified update",
                "url": "https://unknown-blog.test/update",
                "snippet": "Anonymous sources say changes are coming.",
            },
        ],
    )

    labels = {item["credibility"] for item in evidence.source_credibility}
    assert "untrusted" in labels
    assert "weak" in labels
    assert evidence.confidence == EvidenceConfidence.LOW
    assert any("Source credibility signals" in item for item in evidence.unclear)


def test_search_synthesis_marks_provider_degraded_low_confidence():
    evidence = synthesize_search_evidence(
        query="latest energy market update",
        results=[
            {
                "title": "Energy market update",
                "url": "https://reuters.com/business/energy",
                "snippet": "Markets moved after a policy update.",
            }
        ],
        provider_status="degraded",
    )

    assert evidence.provider_status == "degraded"
    assert evidence.confidence == EvidenceConfidence.MEDIUM
    assert any("provider response was degraded" in item for item in evidence.unclear)
