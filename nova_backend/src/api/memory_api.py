from __future__ import annotations

from fastapi import APIRouter

from src.memory.governed_memory_store import GovernedMemoryStore


def build_memory_router(deps) -> APIRouter:
    router = APIRouter()

    @router.get("/api/memory/export")
    async def export_memory():
        payload = GovernedMemoryStore().export_payload()
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "MEMORY_EXPORT_REQUESTED",
            {
                "item_count": int(payload.get("item_count") or 0),
                "includes_deleted": bool(payload.get("includes_deleted")),
                "source": "memory_page",
            },
        )
        return payload

    return router
