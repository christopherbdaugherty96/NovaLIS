

def test_safety_filter_appends_disclaimer_on_action_language():
    from src.conversation.safety_filter import SafetyFilter
    text = "I can search for that and open a website for you."

    filtered = SafetyFilter.filter(text)

    assert "cannot perform actions myself" in filtered
