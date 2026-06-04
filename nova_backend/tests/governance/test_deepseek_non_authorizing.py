from pathlib import Path

DEEPSEEK_BRIDGE_PATH = Path(__file__).resolve().parents[2] / "src" / "conversation" / "deepseek_bridge.py"


def test_deepseek_bridge_has_no_authority_imports_or_network_mediator_calls():
    text = DEEPSEEK_BRIDGE_PATH.read_text(encoding="utf-8", errors="replace")

    forbidden_snippets = [
        "src.governor.governor",
        "src.governor.governor_mediator",
        "src.executors",
        "network_mediator",
        "requests.",
    ]

    for snippet in forbidden_snippets:
        assert snippet not in text, f"Forbidden authority surface found in deepseek_bridge: {snippet}"
