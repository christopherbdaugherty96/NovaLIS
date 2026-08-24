import pytest
from src.governor.governor_mediator import GovernorMediator, Invocation


def test_parse_speak_that_invocation():
    inv = GovernorMediator.parse_governed_invocation("speak that")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 18
    assert inv.params == {}


@pytest.mark.parametrize(
    ("prompt", "text"),
    [
        ("speak: Wave C test", "Wave C test"),
        ("say: hello", "hello"),
        ("read aloud: this sentence", "this sentence"),
    ],
)
def test_explicit_tts_text_routes_to_cap18(prompt, text):
    inv = GovernorMediator.parse_governed_invocation(prompt)

    assert isinstance(inv, Invocation)
    assert inv.capability_id == 18
    assert inv.params == {"text": text}
