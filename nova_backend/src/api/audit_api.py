from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse


def build_audit_router(deps) -> APIRouter:
    router = APIRouter()

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
