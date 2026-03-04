from pathlib import Path
import ast


def test_ollama_chat_only_used_by_llm_gateway():
    root = Path(__file__).resolve().parents[3] / "nova_backend" / "src"
    allowed = {"llm/llm_gateway.py"}
    offenders: list[str] = []

    for path in root.rglob("*.py"):
        rel = path.relative_to(root).as_posix()
        if rel in allowed:
            continue
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        has_direct_ollama = any(
            isinstance(node, ast.Import) and any(alias.name == "ollama" for alias in node.names)
            for node in ast.walk(tree)
        )
        has_direct_chat_call = any(
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "ollama"
            and node.attr == "chat"
            for node in ast.walk(tree)
        )
        if has_direct_ollama or has_direct_chat_call:
            offenders.append(rel)

    assert not offenders, f"Direct ollama usage outside llm gateway: {offenders}"
