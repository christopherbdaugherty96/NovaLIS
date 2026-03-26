from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import FileResponse


def build_workspace_router(deps) -> APIRouter:
    router = APIRouter()

    @router.get("/")
    async def root():
        if deps.INDEX_HTML.exists():
            return FileResponse(deps.INDEX_HTML)
        return {"error": "static/index.html not found"}

    @router.get("/landing")
    async def landing():
        if deps.LANDING_HTML.exists():
            return FileResponse(deps.LANDING_HTML)
        return {"error": "static/landing.html not found"}

    return router
