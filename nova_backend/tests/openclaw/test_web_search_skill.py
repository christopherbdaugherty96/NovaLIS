import asyncio
from unittest.mock import MagicMock, patch

import pytest

from src.skills.web_search import WebSearchSkill, _SearchRequest


# ------------------------------------------------------------------
# can_handle
# ------------------------------------------------------------------

def test_can_handle_search_for():
    skill = WebSearchSkill()
    assert skill.can_handle("search for python tutorials") is True


def test_can_handle_look_up():
    skill = WebSearchSkill()
    assert skill.can_handle("look up weather API") is True


def test_can_handle_search_prefix():
    skill = WebSearchSkill()
    assert skill.can_handle("search latest news") is True


def test_can_handle_negative():
    skill = WebSearchSkill()
    assert skill.can_handle("what time is it") is False


def test_can_handle_empty():
    skill = WebSearchSkill()
    assert skill.can_handle("") is False


# ------------------------------------------------------------------
# _extract_query
# ------------------------------------------------------------------

def test_extract_query_strips_prefix():
    assert WebSearchSkill._extract_query("search for python") == "python"
    assert WebSearchSkill._extract_query("look up weather") == "weather"
    assert WebSearchSkill._extract_query("web search AI agents") == "AI agents"


def test_extract_query_no_prefix():
    assert WebSearchSkill._extract_query("python tutorials") == "python tutorials"


def test_extract_query_empty():
    assert WebSearchSkill._extract_query("") == ""


# ------------------------------------------------------------------
# handle
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_handle_empty_query():
    skill = WebSearchSkill()
    result = await skill.handle("")
    assert result.success is False
    assert "what you'd like" in result.message.lower()


@pytest.mark.asyncio
async def test_handle_successful_search():
    """Mock the executor to return a successful search."""
    skill = WebSearchSkill()

    mock_action_result = MagicMock()
    mock_action_result.success = True
    mock_action_result.message = "Found results for test query"
    mock_action_result.data = {
        "widget": {
            "data": {
                "query": "test",
                "provider": "Brave Search",
                "results": [
                    {"title": "Result 1", "url": "https://example.com", "snippet": "A snippet"},
                ],
                "researched_summary": "Test summary from sources.",
            }
        }
    }

    with patch("src.skills.web_search.WebSearchSkill._execute_search", return_value=MagicMock(
        success=True,
        message="Found results",
        data={"query": "test", "result_count": 1, "results": [], "researched_summary": "Test", "provider": "Brave"},
        widget_data={"type": "search", "data": {}},
        skill="web_search",
    )) as mock_exec:
        result = await skill.handle("search for test")

    assert result.success is True
    assert result.skill == "web_search"


@pytest.mark.asyncio
async def test_handle_search_failure():
    """If executor raises, skill returns graceful failure."""
    skill = WebSearchSkill()

    with patch(
        "src.skills.web_search.WebSearchSkill._execute_search",
        side_effect=RuntimeError("Network down"),
    ):
        result = await skill.handle("search for test")

    assert result.success is False
    assert "unavailable" in result.message.lower()


# ------------------------------------------------------------------
# _SearchRequest duck type
# ------------------------------------------------------------------

def test_search_request_fields():
    req = _SearchRequest(capability_id=16, params={"query": "test"}, request_id="r1")
    assert req.capability_id == 16
    assert req.params["query"] == "test"
    assert req.request_id == "r1"
