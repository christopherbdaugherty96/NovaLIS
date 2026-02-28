from src.conversation.response_style_router import ResponseStyle, ResponseStyleRouter


def test_response_style_defaults_to_direct():
    assert ResponseStyleRouter.route("Give me status") == ResponseStyle.DIRECT


def test_response_style_detects_brainstorm_keywords():
    assert ResponseStyleRouter.route("brainstorm ideas for launch") == ResponseStyle.BRAINSTORM


def test_response_style_detects_deep_input():
    assert ResponseStyleRouter.route("deep analysis of this architecture") == ResponseStyle.DEEP


def test_response_style_detects_casual_opener():
    assert ResponseStyleRouter.route("hello") == ResponseStyle.CASUAL
