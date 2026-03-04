from src.conversation.clarify_prompts import CLARIFY_PROMPTS


def test_clarify_prompts_are_single_question_and_deterministic():
    for key, prompt in CLARIFY_PROMPTS.items():
        assert "\n" not in prompt, key
        if key in {"single_turn_yes_no", "ready_prompt"}:
            continue
        assert prompt.count("?") == 1, key
        assert prompt.endswith("?"), key
