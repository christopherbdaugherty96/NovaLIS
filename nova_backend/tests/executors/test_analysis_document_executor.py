from __future__ import annotations

from types import SimpleNamespace


def _request(params: dict):
    return SimpleNamespace(capability_id=54, params=params, request_id="doc-req")


def test_create_document_appends_and_sets_id(monkeypatch):
    from src.executors import analysis_document_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: (
            "Title: AI Geopolitics Outlook\n"
            "Executive Summary: Global policy competition is accelerating.\n"
            "Section 1 - Current State: Major actors are updating policy.\n"
            "Section 2 - Strategic Risks: Fragmented standards can slow deployment.\n"
            "Section 3 - Signals: Export controls remain volatile.\n"
            "Key Risks: Fragmented standards can slow deployment.\n"
            "Key Signals To Watch: Export controls and compute alliances."
        ),
    )

    executor = mod.AnalysisDocumentExecutor()
    result = executor.execute(_request({"action": "create", "topic": "AI geopolitics", "analysis_documents": []}))

    assert result.success is True
    assert "Doc 1" in result.message
    docs = result.data["analysis_documents"]
    assert len(docs) == 1
    assert docs[0]["id"] == 1
    assert docs[0]["sections"]
    assert docs[0]["summary"] == "Global policy competition is accelerating."


def test_create_document_rejects_incomplete_stub(monkeypatch):
    from src.executors import analysis_document_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: "Title: AI Geopolitics in a Global Context",
    )

    executor = mod.AnalysisDocumentExecutor()
    result = executor.execute(_request({"action": "create", "topic": "AI geopolitics", "analysis_documents": []}))

    assert result.success is False
    assert "incomplete document" in result.message.lower()


def test_summarize_doc_and_explain_section(monkeypatch):
    from src.executors import analysis_document_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: "Main point: regulation pressure is rising.",
    )

    docs = [
        {
            "id": 2,
            "title": "AI Strategic Report",
            "topic": "AI regulation",
            "content": "Section 1 - Landscape\nDetails",
            "summary": "Regulatory activity is increasing.",
            "sections": [
                {"number": 1, "title": "Landscape", "content": "Multiple jurisdictions expanded review scopes."},
                {"number": 3, "title": "Market Effects", "content": "Compliance costs are expected to rise."},
            ],
        }
    ]

    executor = mod.AnalysisDocumentExecutor()

    summarized = executor.execute(_request({"action": "summarize_doc", "doc_id": 2, "analysis_documents": docs}))
    assert summarized.success is True
    assert "Document Summary - Doc 2" in summarized.message

    explained = executor.execute(
        _request({"action": "explain_section", "doc_id": 2, "section_number": 3, "analysis_documents": docs})
    )
    assert explained.success is True
    assert "Section Explanation - Doc 2 Section 3" in explained.message


def test_list_documents_and_missing_doc():
    from src.executors.analysis_document_executor import AnalysisDocumentExecutor

    executor = AnalysisDocumentExecutor()
    listed = executor.execute(
        _request(
            {
                "action": "list",
                "analysis_documents": [{"id": 1, "title": "Doc One"}, {"id": 4, "title": "Doc Four"}],
            }
        )
    )
    assert listed.success is True
    assert "Doc 1" in listed.message
    assert "Doc 4" in listed.message

    missing = executor.execute(_request({"action": "summarize_doc", "doc_id": 99, "analysis_documents": []}))
    assert missing.success is False
    assert "couldn't find" in missing.message.lower()


def test_create_document_fails_truthfully_when_analysis_is_unavailable(monkeypatch):
    from src.executors import analysis_document_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: (
            "I can provide structured analysis, but it is currently unavailable."
        ),
    )

    executor = mod.AnalysisDocumentExecutor()
    result = executor.execute(_request({"action": "create", "topic": "AI geopolitics", "analysis_documents": []}))

    assert result.success is False
    assert "structured analysis is currently blocked or unavailable" in result.message.lower()


def test_explain_section_falls_back_to_section_text_when_analysis_is_unavailable(monkeypatch):
    from src.executors import analysis_document_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: (
            "I can provide structured analysis, but it is currently unavailable."
        ),
    )

    docs = [
        {
            "id": 2,
            "title": "AI Strategic Report",
            "topic": "AI regulation",
            "content": "Section 1 - Landscape\nDetails",
            "summary": "Regulatory activity is increasing.",
            "sections": [
                {"number": 1, "title": "Landscape", "content": "Multiple jurisdictions expanded review scopes."},
            ],
        }
    ]

    executor = mod.AnalysisDocumentExecutor()
    explained = executor.execute(
        _request({"action": "explain_section", "doc_id": 2, "section_number": 1, "analysis_documents": docs})
    )

    assert explained.success is True
    assert "Multiple jurisdictions expanded review scopes." in explained.message


def test_extract_sections_supports_single_line_section_format():
    from src.executors.analysis_document_executor import AnalysisDocumentExecutor

    sections = AnalysisDocumentExecutor._extract_sections(
        "Title: AI Geopolitics Analysis Document\n"
        "Executive Summary: Summary.\n"
        "Section 1 - Introduction: Intro body.\n"
        "Section 2 - Strategy: Strategy body.\n"
        "Section 3 - Risks: Risks body.\n"
        "Key Risks: Some risk.\n"
        "Key Signals To Watch: Some signal."
    )

    assert len(sections) == 3
    assert sections[0]["title"] == "Introduction"
    assert sections[0]["content"] == "Intro body."
