from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.governor.git_child_admission import (
    GitIdentityOperation,
    GitIdentityProbe,
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


async def _runtime_build_identity(probe: GitIdentityProbe) -> dict[str, object]:
    """Return local-only provenance for the source tree serving this process."""
    identity = _unavailable_build_identity()
    results = await probe.read(timeout=_IDENTITY_WAIT_SECONDS)
    if results is None:
        return identity
    commit = results[GitIdentityOperation.COMMIT].stdout.strip()
    unstaged = results[GitIdentityOperation.UNSTAGED]
    staged = results[GitIdentityOperation.STAGED]
    untracked = results[GitIdentityOperation.UNTRACKED].stdout

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
    identity_probe = GitIdentityProbe(_SOURCE_ROOT)

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
            "build_identity": await _runtime_build_identity(identity_probe),
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
