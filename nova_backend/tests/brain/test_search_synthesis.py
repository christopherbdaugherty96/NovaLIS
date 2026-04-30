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
                "url": "https://example.com/models",
                "snippet": "Several AI labs announced new models.",
            },
            {
                "title": "AI release notes",
                "url": "https://example.org/releases",
                "snippet": "New reasoning and coding models shipped.",
            },
        ],
        source_packets=[
            {
                "title": "Model launch roundup",
                "url": "https://example.com/models",
                "text": "Lab A announced a new reasoning model this week. Details may change.",
            },
            {
                "title": "AI release notes",
                "url": "https://example.org/releases",
                "text": "Lab B released a coding model for developers.",
            },
        ],
    )

    assert evidence.evidence_status == "source_backed"
    assert evidence.confidence == EvidenceConfidence.HIGH
    assert evidence.source_pages_read == 2
    assert evidence.result_count == 2
    assert evidence.source_urls == ["https://example.com/models", "https://example.org/releases"]
    assert evidence.claims[0].source_url == "https://example.com/models"
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
