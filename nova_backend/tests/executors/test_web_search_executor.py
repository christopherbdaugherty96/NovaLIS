from unittest.mock import Mock

import pytest


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
    assert "No search query provided" in result.message
    assert result.data["widget"]["data"]["results"] == []


def test_successful_search_returns_results(executor, mock_network, sample_request):
    mock_network.request.return_value = {
        "status_code": 200,
        "data": {
            "Abstract": "This is a very long abstract that definitely exceeds one hundred characters so we can test truncation logic properly.",
            "AbstractURL": "https://example.com/abs",
            "RelatedTopics": [
                {"FirstURL": "https://example.com/rel1", "Text": "Related topic one"},
                {
                    "Topics": [
                        {
                            "FirstURL": "https://example.com/sub1",
                            "Text": "Sub topic inside a category",
                        }
                    ]
                },
            ],
        },
    }

    result = executor.execute(sample_request)

    assert result.success
    assert "I found 3 results" in result.message
    widget = result.data.get("widget", {})
    assert widget["type"] == "search"
    results = widget["data"]["results"]
    assert len(results) == 3
    assert results[0]["title"].endswith("…")
    assert len(results[0]["title"]) <= 100
    assert results[1]["title"] == "Related topic one"


def test_no_results_returns_empty_widget(executor, mock_network, sample_request):
    mock_network.request.return_value = {"status_code": 200, "data": {}}

    result = executor.execute(sample_request)

    assert result.success
    assert "No results found" in result.message
    assert result.data["widget"]["data"]["results"] == []


def test_202_response_returns_failure_with_empty_widget(executor, mock_network, sample_request):
    mock_network.request.return_value = {"status_code": 202, "data": None}

    result = executor.execute(sample_request)

    assert not result.success
    assert "temporarily unavailable" in result.message.lower()
    assert result.data["widget"]["data"]["results"] == []


def test_non_200_status_returns_failure_with_empty_widget(executor, mock_network, sample_request):
    mock_network.request.return_value = {"status_code": 500, "data": {}}

    result = executor.execute(sample_request)

    assert not result.success
    assert "unexpected response" in result.message.lower()
    assert result.data["widget"]["data"]["results"] == []


def test_retry_on_network_error_then_success(executor, mock_network, sample_request):
    from src.governor.exceptions import NetworkMediatorError

    mock_network.request.side_effect = [
        NetworkMediatorError("Timeout"),
        {
            "status_code": 200,
            "data": {"Abstract": "Success after retry", "AbstractURL": "http://example.com"},
        },
    ]

    result = executor.execute(sample_request)

    assert result.success
    assert mock_network.request.call_count == 2


def test_retry_on_network_error_then_failure(executor, mock_network, sample_request):
    from src.governor.exceptions import NetworkMediatorError

    mock_network.request.side_effect = NetworkMediatorError("Timeout")

    result = executor.execute(sample_request)

    assert not result.success
    assert "network issue" in result.message.lower()
    assert mock_network.request.call_count == 2


def test_retry_does_not_occur_on_success(executor, mock_network, sample_request):
    mock_network.request.return_value = {"status_code": 200, "data": {}}

    result = executor.execute(sample_request)

    assert result.success
    assert mock_network.request.call_count == 1


def test_non_200_does_not_trigger_retry(executor, mock_network, sample_request):
    mock_network.request.return_value = {"status_code": 500, "data": {}}

    result = executor.execute(sample_request)

    assert not result.success
    assert "unexpected response" in result.message.lower()
    assert mock_network.request.call_count == 1
