from __future__ import annotations

from pathlib import Path
import sys
import inspect
import ast

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.conversation.escalation_policy import EscalationPolicy

GENERAL_CHAT_PATH = PROJECT_ROOT / "src" / "skills" / "general_chat.py"


def test_escalation_policy_remains_non_authorizing():
    """
    Escalation may return ALLOW automatically (cognitive autonomy allowed),
    but it must not directly reference or invoke any execution surface.
    """
    policy = EscalationPolicy()

    heuristic_result = {
        "escalate": True,
        "reason_codes": ["DEPTH_KEYWORD"],
        "suggested_max_tokens": 800,
    }

    session_state = {
        "turn_count": 5,
        "last_escalation_turn": None,
        "escalation_count": 0,
        "deep_mode_disabled": False,
        "explicit_deep_thought_requested": False,
    }

    decision = policy.decide(heuristic_result, "analyze this deeply", session_state)

    # Escalation can ALLOW, but must not perform authority actions
    assert decision in {"ALLOW", "ALLOW_ANALYSIS_ONLY", "DENY"}

    # Ensure no execution surfaces referenced inside policy module
    source = inspect.getsource(EscalationPolicy)
    forbidden_tokens = [
        "handle_governed_invocation",
        "execute_",
        "Invocation(",
        "capability_id=",
        "Governor",
    ]

    for token in forbidden_tokens:
        assert token not in source, f"Found forbidden token '{token}' in EscalationPolicy source"


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