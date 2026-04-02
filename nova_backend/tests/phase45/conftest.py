from __future__ import annotations

from pathlib import Path

import pytest

# Resolve the Nova-Project root relative to this file's location.
# Main repo layout:     .../Nova-Project/nova_backend/tests/phase45/conftest.py
#                       parents: [phase45, tests, nova_backend, Nova-Project, ...]
# Git worktree layout:  .../Nova-Project/.claude/worktrees/<name>/nova_backend/tests/phase45/conftest.py
#                       parents: [..., Nova-Project, .claude, worktrees, <name>, nova_backend, tests, phase45]
# In both cases, searching for "Nova-Project" in parents finds the correct root.
_HERE = Path(__file__).resolve()
NOVA_PROJECT_ROOT = next(
    (p for p in _HERE.parents if p.name == "Nova-Project"),
    _HERE.parents[3],  # fallback: .../nova_backend/tests/phase45 → nova_backend parent
)


@pytest.fixture(autouse=True)
def _inject_nova_project_root_candidate(monkeypatch):
    """Ensure C:\\Nova-Project is always the first candidate local project path.

    In git worktree environments, Path.cwd() resolves to the worktree directory
    rather than the main repository root. Tests that resolve 'Nova-Project' by
    name (e.g. 'audit folder Nova-Project', 'open folder Nova-Project') or
    by current-workspace alias (e.g. 'open this repo') rely on this candidate
    being present and first in the list.
    """
    from src.utils import path_resolver as _pr

    _orig = _pr._candidate_local_project_paths

    def _patched(working_context, session_state):
        candidates = list(_orig(working_context, session_state))
        if NOVA_PROJECT_ROOT.exists() and NOVA_PROJECT_ROOT not in candidates:
            candidates = [NOVA_PROJECT_ROOT] + candidates
        elif NOVA_PROJECT_ROOT.exists() and candidates and candidates[0] != NOVA_PROJECT_ROOT:
            candidates = [NOVA_PROJECT_ROOT] + [c for c in candidates if c != NOVA_PROJECT_ROOT]
        return candidates

    monkeypatch.setattr(_pr, "_candidate_local_project_paths", _patched)
