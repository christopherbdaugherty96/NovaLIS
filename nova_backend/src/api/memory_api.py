from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from src.memory.governed_memory_store import GovernedMemoryStore
from src.memory.user_memory_store import user_memory_store
from src.memory.nova_self_memory_store import nova_self_memory_store


def build_memory_router(deps) -> APIRouter:
    router = APIRouter()

    # ── Governed Memory (explicit saves) ────────────────────────────

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

    # ── User Memory (preferences, personal details) ─────────────────

    @router.get("/api/memory/user")
    async def get_user_memories():
        """List all user memory entries grouped by category."""
        entries = user_memory_store.get_all(limit=100)
        return {
            "entries": entries,
            "snapshot": user_memory_store.snapshot(),
        }

    @router.get("/api/memory/user/search")
    async def search_user_memories(q: str = ""):
        """Search user memories by keyword."""
        if not q.strip():
            return {"entries": [], "query": ""}
        entries = user_memory_store.search(q.strip(), limit=20)
        return {"entries": entries, "query": q.strip()}

    @router.get("/api/memory/user/category/{category}")
    async def get_user_memories_by_category(category: str):
        """List user memories for a specific category."""
        entries = user_memory_store.get_by_category(category, limit=50)
        return {"entries": entries, "category": category}

    @router.post("/api/memory/user")
    async def save_user_memory(payload: dict[str, Any]):
        """Save or update a user memory entry."""
        category = str(payload.get("category") or "").strip()
        key = str(payload.get("key") or "").strip()
        value = str(payload.get("value") or "").strip()
        if not category or not key or not value:
            raise HTTPException(status_code=400, detail="category, key, and value are required.")
        entry = user_memory_store.save(
            category,
            key,
            value,
            context=str(payload.get("context") or "").strip(),
            source="explicit",
            confidence=1.0,
        )
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "USER_MEMORY_SAVED",
            {
                "entry_id": str(entry.get("id") or ""),
                "category": category,
                "key": key,
                "source": "memory_api",
            },
        )
        return {"entry": entry, "snapshot": user_memory_store.snapshot()}

    @router.delete("/api/memory/user/{entry_id}")
    async def delete_user_memory(entry_id: str):
        """Delete a specific user memory entry."""
        deleted = user_memory_store.remove(entry_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Memory entry not found.")
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "USER_MEMORY_DELETED",
            {
                "entry_id": entry_id,
                "source": "memory_api",
            },
        )
        return {"deleted": True, "entry_id": entry_id, "snapshot": user_memory_store.snapshot()}

    # ── Nova Self Memory (relationship context) ─────────────────────

    @router.get("/api/memory/nova")
    async def get_nova_self_memory():
        """View Nova's self-memory: relationship insights, session summaries, topic patterns."""
        return {
            "relationship_context": nova_self_memory_store.get_relationship_context(max_chars=500),
            "recent_summaries": nova_self_memory_store.get_recent_summaries(limit=5),
            "top_topics": [
                {"topic": t, "count": c}
                for t, c in nova_self_memory_store.get_top_topics(limit=10)
            ],
            "snapshot": nova_self_memory_store.snapshot(),
        }

    # ── Combined memory context (what Nova currently knows) ─────────

    @router.get("/api/memory/context")
    async def get_memory_context():
        """Preview the memory context block that gets injected into prompts."""
        user_ctx = user_memory_store.render_context_block(max_chars=400)
        relationship_ctx = nova_self_memory_store.get_relationship_context(max_chars=200)
        return {
            "user_context": user_ctx,
            "relationship_context": relationship_ctx,
            "user_snapshot": user_memory_store.snapshot(),
            "nova_snapshot": nova_self_memory_store.snapshot(),
        }

    return router
