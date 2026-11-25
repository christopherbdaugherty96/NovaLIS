from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.governor.git_child_admission import (
    GitChildAdmissionError,
    GitIdentityOperation,
    run_git_identity_plan,
)


_IDENTITY_WAIT_SECONDS = 1.0
_SOURCE_ROOT = Path(__file__).resolve().parents[3]


def _unavailable_build_identity() -> dict[str, object]:
    return {
        "source_root": str(_SOURCE_ROOT),
        "commit_sha": None,
        "working_tree_dirty": None,
        "git_available": False,
    }


def _runtime_build_identity() -> dict[str, object]:
    """Return local-only provenance for the source tree serving this process."""
    identity = _unavailable_build_identity()
    try:
        results = run_git_identity_plan(_SOURCE_ROOT)
        commit = results[GitIdentityOperation.COMMIT].stdout.strip()
        unstaged = results[GitIdentityOperation.UNSTAGED]
        staged = results[GitIdentityOperation.STAGED]
        untracked = results[GitIdentityOperation.UNTRACKED].stdout
    except GitChildAdmissionError:
        return identity

    if unstaged.returncode not in {0, 1} or staged.returncode not in {0, 1}:
        return identity

    identity.update(
        {
            "commit_sha": commit or None,
            "working_tree_dirty": bool(
                unstaged.returncode or staged.returncode or untracked.strip()
            ),
            "git_available": True,
        }
    )
    return identity


def build_audit_router(deps) -> APIRouter:
    router = APIRouter()
    identity_task: asyncio.Task[dict[str, object]] | None = None

    async def build_identity() -> dict[str, object]:
        nonlocal identity_task
        if identity_task is None or identity_task.done():
            identity_task = asyncio.create_task(asyncio.to_thread(_runtime_build_identity))
        # A caller timing out or cancelling must leave the shared worker tracked.
        try:
            return await asyncio.wait_for(
                asyncio.shield(identity_task), timeout=_IDENTITY_WAIT_SECONDS
            )
        except asyncio.TimeoutError:
            return _unavailable_build_identity()

    @router.get("/phase-status")
    async def phase_status():
        from src.governor.execute_boundary import GOVERNED_ACTIONS_ENABLED

        build_phase = deps.BUILD_PHASE
        phase_display = (
            "7 complete / 8 active"
            if build_phase >= 8
            else
            "7 complete / 8 design"
            if build_phase >= 7
            else "6 complete / 7 partial"
            if build_phase >= 6
            else "5 closed / 6 foundation"
            if build_phase >= 5
            else f"{build_phase}"
        )
        return {
            "phase": str(build_phase),
            "phase_display": phase_display,
            "status": "active" if GOVERNED_ACTIONS_ENABLED else "sealed",
            "execution_enabled": GOVERNED_ACTIONS_ENABLED,
            "delegated_runtime_enabled": False,
            "build_identity": await build_identity(),
            "note": (
                "Phase-7 governed external reasoning is complete in the current runtime. "
                "Second opinions stay advisory only, and delegated execution remains disabled."
            ),
        }

    @router.get("/system/audit/runtime-truth")
    async def audit_runtime_truth():
        return deps.run_runtime_truth_audit()

    @router.get("/system/audit/runtime-truth.md", response_class=PlainTextResponse)
    async def audit_runtime_truth_markdown():
        report = deps.run_runtime_truth_audit()
        return deps.render_runtime_truth_markdown(report)

    return router
