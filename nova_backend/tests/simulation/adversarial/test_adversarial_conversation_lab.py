from __future__ import annotations

from .adversarial_conversation_lab import (
    DEFAULT_ADVERSARIAL_CASES,
    assert_case_hardened,
    run_adversarial_case,
)


def test_adversarial_conversation_lab_cases():
    for case in DEFAULT_ADVERSARIAL_CASES:
        transcript = run_adversarial_case(case)
        assert_case_hardened(case, transcript)

