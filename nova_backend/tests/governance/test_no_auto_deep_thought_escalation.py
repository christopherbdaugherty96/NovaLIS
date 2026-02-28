from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import ast

from src.conversation.escalation_policy import EscalationPolicy

GENERAL_CHAT_PATH = PROJECT_ROOT / "src" / "skills" / "general_chat.py"


def test_escalation_policy_requires_explicit_user_intent_for_allow():
    policy = EscalationPolicy()
    heuristic_result = {"escalate": True, "reason_codes": ["DEPTH_KEYWORD"], "suggested_max_tokens": 800}
    session_state = {
        "turn_count": 5,
        "last_escalation_turn": None,
        "escalation_count": 0,
        "deep_mode_disabled": False,
        # Explicit user intent flag not present / false
        "explicit_deep_thought_requested": False,
    }

    decision = policy.decide(heuristic_result, "analyze this deeply", session_state)
    assert decision != "ALLOW", (
        "EscalationPolicy returned ALLOW without explicit user intent flag; "
        "automatic deep-thought escalation is prohibited."
    )


def test_general_chat_does_not_auto_call_deepseek_process():
    tree = ast.parse(GENERAL_CHAT_PATH.read_text(encoding="utf-8", errors="replace"), filename=str(GENERAL_CHAT_PATH))
    offenders: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "self" and node.func.attr == "deepseek":
                offenders.append(f"{GENERAL_CHAT_PATH}:{node.lineno} direct self.deepseek(...) call")
            chain = []
            cur = node.func
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                chain.append(cur.id)
            dotted = ".".join(reversed(chain))
            if dotted == "self.deepseek.process":
                offenders.append(f"{GENERAL_CHAT_PATH}:{node.lineno} self.deepseek.process auto-invocation")

    assert not offenders, "\n".join(offenders)
