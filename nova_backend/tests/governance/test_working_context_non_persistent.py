from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKING_CONTEXT_ROOT = PROJECT_ROOT / "src" / "working_context"


def test_working_context_modules_do_not_write_persistent_storage_or_spawn_threads():
    offenders: list[str] = []

    for py_file in sorted(WORKING_CONTEXT_ROOT.glob("*.py")):
        source = py_file.read_text(encoding="utf-8", errors="replace")
        lowered = source.lower()
        tree = ast.parse(source, filename=str(py_file))

        for marker in ("write_text(", "json.dump(", "sqlite3", "threading.thread", "create_task("):
            if marker in lowered:
                offenders.append(f"{py_file}: forbidden marker '{marker}'")

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {"open"}:
                    offenders.append(f"{py_file}:{node.lineno} direct open() call")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {"write", "writelines"}:
                    offenders.append(f"{py_file}:{node.lineno} write call detected")

    assert not offenders, "\n".join(offenders)


def test_brain_server_contains_working_context_session_state():
    # brain_server.py declares WorkingContextStore and the "working_context" session key.
    # The live session wiring (including working_context.for_explain()) was extracted to
    # session_handler.py as part of the route-extraction refactor. Both files are checked.
    brain_server_path = PROJECT_ROOT / "src" / "brain_server.py"
    session_handler_path = PROJECT_ROOT / "src" / "websocket" / "session_handler.py"
    brain_source = brain_server_path.read_text(encoding="utf-8", errors="replace")
    session_source = session_handler_path.read_text(encoding="utf-8", errors="replace")
    assert "WorkingContextStore" in brain_source
    assert '"working_context"' in brain_source
    # for_explain() is called in the session handler where explain capability params are enriched
    assert "working_context.for_explain()" in session_source
