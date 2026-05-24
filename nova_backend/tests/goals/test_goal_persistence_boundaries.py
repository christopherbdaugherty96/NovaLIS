# tests/goals/test_goal_persistence_boundaries.py
"""
Goal persistence boundary tests.

These tests enforce the design doc invariants:

  1. Saving a goal never executes an action.
  2. Loading a goal never executes an action.
  3. Updating a goal status never executes an action.
  4. Goal persistence code never imports GovernorMediator.
  5. Goal persistence code never imports any executor.
  6. Goal persistence code never calls the ledger.
  7. The word "schedule" does not appear in goal persistence code.
  8. DISPLAY ONLY badge remains on the Goals page.

Additionally:
  - API does not expose /run, /execute, or /schedule endpoints.
  - No execution_schedule, trigger, automation_config, or
    background_run fields exist in the data model.
"""
import ast
import pytest
from pathlib import Path


# ── source paths ────────────────────────────────────

_GOALS_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "src" / "goals"
)
_GOALS_API = (
    Path(__file__).resolve().parent.parent.parent
    / "src" / "api" / "goals_api.py"
)
_GOAL_STORE = _GOALS_DIR / "goal_store.py"
_PERSISTENCE_SOURCES = [_GOAL_STORE, _GOALS_API]


def _read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_imports(source_text: str) -> list[str]:
    """Extract all import module paths using AST."""
    tree = ast.parse(source_text)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def _extract_code_lines(source_text: str) -> list[tuple[int, str]]:
    """
    Return (line_number, text) for lines that are actual code —
    not inside docstrings, not comments, not blank.
    """
    tree = ast.parse(source_text)
    # Collect line ranges of all string-expression nodes (docstrings)
    docstring_lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(
            node.value, (ast.Constant, ast.Str)
        ):
            for lineno in range(node.lineno, node.end_lineno + 1):
                docstring_lines.add(lineno)

    lines = source_text.split("\n")
    result = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if i in docstring_lines:
            continue
        result.append((i, stripped))
    return result


def _extract_route_decorators(source_text: str) -> list[str]:
    """Extract all route path strings from @router decorators."""
    import re
    # Match patterns like @router.get("/api/goals") etc.
    pattern = r'@router\.\w+\(\s*["\']([^"\']+)["\']'
    return re.findall(pattern, source_text)


# ── invariant 4: no GovernorMediator import ─────────


class TestNoGovernorMediatorImport:
    @pytest.mark.parametrize("source", _PERSISTENCE_SOURCES)
    def test_no_governor_import(self, source):
        imports = _extract_imports(_read_source(source))
        for imp in imports:
            assert "governor" not in imp.lower(), (
                f"{source.name} imports governor module: {imp}"
            )


# ── invariant 5: no executor import ────────────────


class TestNoExecutorImport:
    @pytest.mark.parametrize("source", _PERSISTENCE_SOURCES)
    def test_no_executor_import(self, source):
        imports = _extract_imports(_read_source(source))
        for imp in imports:
            assert "executor" not in imp.lower(), (
                f"{source.name} imports executor module: {imp}"
            )

    @pytest.mark.parametrize("source", _PERSISTENCE_SOURCES)
    def test_no_executor_reference_in_code(self, source):
        for lineno, line in _extract_code_lines(
            _read_source(source)
        ):
            assert "executor" not in line.lower(), (
                f"{source.name}:{lineno} references executor: "
                f"{line!r}"
            )


# ── invariant 6: no ledger calls ────────────────────


class TestNoLedgerCalls:
    @pytest.mark.parametrize("source", _PERSISTENCE_SOURCES)
    def test_no_ledger_import(self, source):
        imports = _extract_imports(_read_source(source))
        for imp in imports:
            assert "ledger" not in imp.lower(), (
                f"{source.name} imports ledger module: {imp}"
            )

    @pytest.mark.parametrize("source", _PERSISTENCE_SOURCES)
    def test_no_ledger_reference_in_code(self, source):
        for lineno, line in _extract_code_lines(
            _read_source(source)
        ):
            # ledger_refs is a data field name — allowed
            cleaned = line.replace("ledger_refs", "")
            cleaned = cleaned.replace('"ledger_refs"', "")
            assert "ledger" not in cleaned.lower(), (
                f"{source.name}:{lineno} references ledger: "
                f"{line!r}"
            )


# ── invariant 7: no "schedule" in persistence code ──


class TestNoScheduleWord:
    @pytest.mark.parametrize("source", _PERSISTENCE_SOURCES)
    def test_no_schedule_in_code(self, source):
        for lineno, line in _extract_code_lines(
            _read_source(source)
        ):
            assert "schedule" not in line.lower(), (
                f"{source.name}:{lineno} contains 'schedule': "
                f"{line!r}"
            )


# ── API does not expose execution endpoints ─────────


class TestNoExecutionEndpoints:
    def test_no_run_route(self):
        routes = _extract_route_decorators(_read_source(_GOALS_API))
        for route in routes:
            assert "/run" not in route, (
                f"goals_api.py exposes a /run route: {route}"
            )

    def test_no_execute_route(self):
        routes = _extract_route_decorators(_read_source(_GOALS_API))
        for route in routes:
            assert "/execute" not in route, (
                f"goals_api.py exposes an /execute route: {route}"
            )

    def test_no_schedule_route(self):
        routes = _extract_route_decorators(_read_source(_GOALS_API))
        for route in routes:
            assert "/schedule" not in route, (
                f"goals_api.py exposes a /schedule route: {route}"
            )

    def test_no_delete_decorator(self):
        import re
        text = _read_source(_GOALS_API)
        assert not re.search(
            r'@router\.delete\(', text
        ), "goals_api.py must not have a DELETE endpoint"

    def test_only_expected_routes(self):
        routes = _extract_route_decorators(_read_source(_GOALS_API))
        expected = {
            "/api/goals",
            "/api/goals/{goal_id}",
        }
        assert set(routes) == expected, (
            f"Unexpected routes: {set(routes) - expected}"
        )


# ── no forbidden data model fields ──────────────────


class TestNoForbiddenFields:
    _FORBIDDEN = [
        "execution_schedule",
        "trigger",
        "automation_config",
        "background_run",
    ]

    @pytest.mark.parametrize("field", _FORBIDDEN)
    def test_forbidden_field_not_in_store(self, field):
        for lineno, line in _extract_code_lines(
            _read_source(_GOAL_STORE)
        ):
            assert field not in line, (
                f"goal_store.py:{lineno} contains {field!r}"
            )

    @pytest.mark.parametrize("field", _FORBIDDEN)
    def test_forbidden_field_not_in_api(self, field):
        for lineno, line in _extract_code_lines(
            _read_source(_GOALS_API)
        ):
            assert field not in line, (
                f"goals_api.py:{lineno} contains {field!r}"
            )


# ── invariant 8: DISPLAY ONLY badge ────────────────


class TestDisplayOnlyBadge:
    def test_display_only_badge_in_index_html(self):
        index_path = (
            Path(__file__).resolve().parent.parent.parent
            / "static" / "index.html"
        )
        text = index_path.read_text(encoding="utf-8")
        assert "Display only" in text, (
            "index.html must still contain the 'Display only' badge"
        )


# ── runtime invariants 1-3: CRUD does not execute ──


class TestCrudDoesNotExecute:
    """
    Prove that create/read/update operations are pure state
    operations with no side effects beyond file I/O.
    """

    def test_create_does_not_import_executor(self, tmp_path):
        import sys
        from src.goals.goal_store import GoalStore

        store = GoalStore(path=tmp_path / "goals.json")

        before = set(sys.modules.keys())
        store.create_goal({"title": "Safe goal"})
        after = set(sys.modules.keys())

        new_modules = after - before
        for mod in new_modules:
            assert "executor" not in mod.lower(), (
                f"create_goal loaded executor module: {mod}"
            )
            assert "governor" not in mod.lower(), (
                f"create_goal loaded governor module: {mod}"
            )

    def test_update_does_not_import_executor(self, tmp_path):
        import sys
        from src.goals.goal_store import GoalStore

        store = GoalStore(path=tmp_path / "goals.json")
        store.create_goal({
            "goal_id": "g1",
            "title": "Update test",
        })

        before = set(sys.modules.keys())
        store.update_goal("g1", {"status": "completed"})
        after = set(sys.modules.keys())

        new_modules = after - before
        for mod in new_modules:
            assert "executor" not in mod.lower()
            assert "governor" not in mod.lower()

    def test_list_does_not_import_executor(self, tmp_path):
        import sys
        from src.goals.goal_store import GoalStore

        store = GoalStore(path=tmp_path / "goals.json")
        store.create_goal({"title": "List test"})

        before = set(sys.modules.keys())
        store.list_goals()
        after = set(sys.modules.keys())

        new_modules = after - before
        for mod in new_modules:
            assert "executor" not in mod.lower()
            assert "governor" not in mod.lower()


# ── goals API is local-only ─────────────────────────


class TestGoalsApiLocalOnly:
    def test_goals_prefix_in_local_guard(self):
        from src.utils.local_request_guard import (
            _LOCAL_ONLY_API_PREFIXES,
        )
        assert any(
            p.startswith("/api/goals")
            for p in _LOCAL_ONLY_API_PREFIXES
        ), "/api/goals must be in the local-only API prefix list"
