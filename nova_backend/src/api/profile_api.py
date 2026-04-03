from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from src.profiles.user_profile_store import user_profile_store


def build_profile_router(deps: Any) -> APIRouter:
    router = APIRouter()

    # ------------------------------------------------------------------
    # GET /api/profile
    # ------------------------------------------------------------------

    @router.get("/api/profile")
    async def get_profile():
        """Return the current user profile snapshot."""
        return user_profile_store.snapshot()

    # ------------------------------------------------------------------
    # POST /api/profile/identity
    # ------------------------------------------------------------------

    @router.post("/api/profile/identity")
    async def set_identity(payload: dict[str, Any]):
        """Save name, nickname, and email. Writes user_identity to memory."""
        name = payload.get("name")
        nickname = payload.get("nickname")
        email = payload.get("email")

        if name is not None and not isinstance(name, str):
            raise HTTPException(status_code=400, detail="name must be a string")
        if nickname is not None and not isinstance(nickname, str):
            raise HTTPException(status_code=400, detail="nickname must be a string")
        if email is not None and not isinstance(email, str):
            raise HTTPException(status_code=400, detail="email must be a string")

        snapshot = user_profile_store.set_identity(
            name=name,
            nickname=nickname,
            email=email,
        )

        _write_identity_to_memory()

        try:
            deps._log_ledger_event(
                deps.RUNTIME_GOVERNOR,
                "USER_PROFILE_IDENTITY_SAVED",
                {"name_set": bool(name), "nickname_set": bool(nickname), "email_set": bool(email)},
            )
        except Exception:
            pass

        return snapshot

    # ------------------------------------------------------------------
    # POST /api/profile/preferences
    # ------------------------------------------------------------------

    @router.post("/api/profile/preferences")
    async def set_preferences(payload: dict[str, Any]):
        """Save preference toggles (response style, name usage, suggestions, brief)."""
        try:
            snapshot = user_profile_store.set_preferences(
                response_style=payload.get("response_style"),
                use_name_in_responses=payload.get("use_name_in_responses"),
                proactive_suggestions=payload.get("proactive_suggestions"),
                morning_brief_enabled=payload.get("morning_brief_enabled"),
                morning_brief_time=payload.get("morning_brief_time"),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        _write_identity_to_memory()

        try:
            deps._log_ledger_event(
                deps.RUNTIME_GOVERNOR,
                "USER_PROFILE_PREFERENCES_SAVED",
                {"keys": list(payload.keys())},
            )
        except Exception:
            pass

        return snapshot

    # ------------------------------------------------------------------
    # POST /api/profile/rules
    # ------------------------------------------------------------------

    @router.post("/api/profile/rules")
    async def set_rules(payload: dict[str, Any]):
        """Save the user's custom rules for Nova behaviour."""
        rules = payload.get("rules", "")
        if not isinstance(rules, str):
            raise HTTPException(status_code=400, detail="rules must be a string")

        snapshot = user_profile_store.set_rules(rules)
        _write_identity_to_memory()

        try:
            deps._log_ledger_event(
                deps.RUNTIME_GOVERNOR,
                "USER_PROFILE_RULES_SAVED",
                {"rules_length": len(rules)},
            )
        except Exception:
            pass

        return snapshot

    return router


# ------------------------------------------------------------------
# Memory write helper
# ------------------------------------------------------------------

def _write_identity_to_memory() -> None:
    """Write (or overwrite) the protected user_identity memory record.

    Errors are swallowed — profile saves must not fail because of memory issues.
    """
    try:
        from src.memory.governed_memory_store import GovernedMemoryStore
        record = user_profile_store.as_memory_record()
        store = GovernedMemoryStore()

        # Check if a user_identity record already exists — if so, supersede it
        existing = store.find_relevant_items("user_identity", limit=5)
        existing_id = None
        for item in existing:
            if item.get("source") == "user_profile_setup":
                existing_id = item.get("id")
                break

        if existing_id:
            # Soft-delete the old one and save fresh
            store.delete_item(existing_id, confirmed=True)

        store.save_item(
            title=record["title"],
            body=record["body"],
            scope=record["scope"],
            source=record["source"],
            tags=["identity", "profile", "user"],
            lock_after_save=True,
        )
    except Exception:
        pass
