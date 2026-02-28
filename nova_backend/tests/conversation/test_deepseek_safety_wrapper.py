from src.conversation.deepseek_safety_wrapper import DeepSeekSafetyWrapper


def test_deepseek_safety_wrapper_strips_action_language_and_tokens():
    wrapper = DeepSeekSafetyWrapper()
    text = "You should run this now. <function_call name='x'/> capability_id: 18"
    clean = wrapper.sanitize(text)

    assert "you should" not in clean.lower()
    assert "run" not in clean.lower()
    assert "function_call" not in clean.lower()
    assert "capability_id" not in clean.lower()
