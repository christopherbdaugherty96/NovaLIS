from src.conversation.conversation_router import ConversationRouter


def test_router_detects_command_and_heavy_ack():
    out = ConversationRouter.route("search latest ai regulation news")
    assert out["mode"] == "command"
    assert out["micro_ack"]


def test_router_requests_clarification_without_context():
    out = ConversationRouter.route("open that file")
    assert out["needs_clarification"] is True
    assert out["clarification"] == "Which file or folder do you mean?"


def test_router_resolves_reference_with_context():
    out = ConversationRouter.route("open that folder", {"last_object": "downloads"})
    assert out["needs_clarification"] is False
    assert "downloads" in out["resolved_text"].lower()
