from unittest.mock import Mock
import pytest


@pytest.fixture(autouse=True)
def configured_brave_key(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")


@pytest.fixture
def mock_network():
    return Mock()


@pytest.fixture
def executor(mock_network):
    from src.executors.web_search_executor import WebSearchExecutor
    from src.governor.execute_boundary import ExecuteBoundary

    return WebSearchExecutor(mock_network, ExecuteBoundary())


@pytest.fixture
def sample_request():
    from src.actions.action_request import ActionRequest
    return ActionRequest(capability_id=16, params={"query": "test query"})


def test_empty_query_returns_failure_with_empty_widget(executor):
    from src.actions.action_request import ActionRequest

    request = ActionRequest(capability_id=16, params={"query": "   "})
    result = executor.execute(request)

    assert not result.success
    assert "what you want me to search for" in result.message
    widget_data = result.data["widget"]["data"]
    assert widget_data["results"] == []
    assert widget_data["query"] == ""
    assert widget_data["result_count"] == 0
    assert isinstance(widget_data["suggested_actions"], list)


def test_successful_search_returns_results(executor, mock_network, sample_request, monkeypatch):
    monkeypatch.setattr(
        "src.executors.web_search_executor.generate_chat",
        lambda *args, **kwargs: "Sourced synthesis: outlet reporting aligns on the primary development.",
    )
    mock_network.request.return_value = {
        "status_code": 200,
        "data": {
            "web": {
                "results": [
                    {
                        "title": "Result one title",
                        "url": "https://example.com/one",
                        "description": "One",
                    },
                    {
                        "title": "Result two title",
                        "url": "https://example.com/two",
                        "description": "Two",
                    },
                    {
                        "title": "Result three title",
                        "url": "https://example.com/three",
                        "description": "Three",
                    },
                ]
            }
        },
    }

    result = executor.execute(sample_request)

    assert result.success
    assert "Key Points" in result.message
    assert "Sources" in result.message
    assert "Confidence" in result.message
    assert "Try next" in result.message

    widget = result.data.get("widget", {})
    assert widget["type"] == "search"

    widget_data = widget["data"]
    results = widget_data["results"]
    assert len(results) == 3
    assert results[0]["title"] == "Result one title"
    assert results[1]["title"] == "Result two title"
    assert widget_data["query"] == "test query"
    assert widget_data["provider"] == "Brave Search"
    assert widget_data["result_count"] == 3
    assert widget_data["summary"]
    assert widget_data["source_pages_read"] >= 0
    assert "researched_summary" in widget_data
    assert isinstance(widget_data["suggested_actions"], list)
    assert widget_data["suggested_actions"]
    assert isinstance(widget_data["follow_up_prompts"], list)


def test_no_results_returns_empty_widget(executor, mock_network, sample_request):
    mock_network.request.return_value = {
        "status_code": 200,
        "data": {"web": {"results": []}},
    }

    result = executor.execute(sample_request)

    assert result.success
    assert "couldn't find solid results" in result.message.lower()
    widget_data = result.data["widget"]["data"]
    assert widget_data["results"] == []
    assert widget_data["query"] == "test query"
    assert widget_data["provider"] == "Brave Search"
    assert widget_data["result_count"] == 0


def test_non_200_status_returns_failure_with_empty_widget(
    executor, mock_network, sample_request
):
    mock_network.request.return_value = {"status_code": 500, "data": {}}

    result = executor.execute(sample_request)

    assert not result.success
    assert "network issue" in result.message.lower()
    widget_data = result.data["widget"]["data"]
    assert widget_data["results"] == []
    assert widget_data["query"] == "test query"


def test_retry_on_network_error_then_success(executor, mock_network, sample_request):
    from src.governor.exceptions import NetworkMediatorError

    mock_network.request.side_effect = [
        NetworkMediatorError("Timeout"),
        {
            "status_code": 200,
            "data": {
                "web": {
                    "results": [
                        {
                            "title": "Success after retry",
                            "url": "http://example.com",
                            "description": "Desc",
                        }
                    ]
                }
            },
        },
    ]

    result = executor.execute(sample_request)

    assert result.success
    assert mock_network.request.call_count >= 2


def test_retry_on_network_error_then_failure(executor, mock_network, sample_request):
    from src.governor.exceptions import NetworkMediatorError

    mock_network.request.side_effect = NetworkMediatorError("Timeout")

    result = executor.execute(sample_request)

    assert not result.success
    assert "network issue" in result.message.lower()
    assert mock_network.request.call_count == 2


def test_missing_brave_api_key_uses_duck_fallback(
    executor, mock_network, sample_request, monkeypatch
):
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    monkeypatch.setattr(
        "src.executors.web_search_executor.generate_chat",
        lambda *args, **kwargs: "Duck-backed synthesis summary.",
    )
    mock_network.request.return_value = {
        "status_code": 200,
        "data": {
            "Abstract": "Duck fallback summary",
            "AbstractURL": "https://duck.example/story",
            "RelatedTopics": [],
        },
    }

    result = executor.execute(sample_request)

    assert result.success is True
    assert "duckduckgo" in result.message.lower()
    assert mock_network.request.call_count >= 1
    widget_data = result.data["widget"]["data"]
    assert widget_data["provider"] == "DuckDuckGo Instant Answer"
    assert widget_data["result_count"] == 1
    assert widget_data["follow_up_prompts"]


def test_search_reads_source_pages_and_uses_researched_summary(executor, mock_network, sample_request, monkeypatch):
    monkeypatch.setattr(
        "src.executors.web_search_executor.generate_chat",
        lambda *args, **kwargs: "Sourced answer based on reviewed pages from example.com and sample.org.",
    )
    mock_network.request.side_effect = [
        {
            "status_code": 200,
            "data": {
                "web": {
                    "results": [
                        {
                            "title": "Result one title",
                            "url": "https://example.com/one",
                            "description": "One",
                        },
                        {
                            "title": "Result two title",
                            "url": "https://sample.org/two",
                            "description": "Two",
                        },
                    ]
                }
            },
        },
        {"status_code": 200, "text": "<html><body><article>First source details.</article></body></html>"},
        {"status_code": 200, "text": "<html><body><article>Second source details.</article></body></html>"},
    ]

    result = executor.execute(sample_request)

    assert result.success
    widget_data = result.data["widget"]["data"]
    assert widget_data["source_pages_read"] == 2
    assert "Sourced answer based on reviewed pages" in widget_data["researched_summary"]
