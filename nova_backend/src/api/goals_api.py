# src/api/goals_api.py
"""
Goal persistence API — CRUD for goal state records.

GET  /api/goals          → list all goals
GET  /api/goals/{id}     → single goal detail
POST /api/goals          → create a new visible goal record
                            from explicit user/conversation context
PUT  /api/goals/{id}     → update goal state (status, steps)

This API does NOT expose:
  /api/goals/{id}/run
  /api/goals/{id}/execute
  /api/goals/{id}/schedule

These endpoints are state storage only. They do not dispatch
actions, call executors, contact the GovernorMediator, or
write to the ledger.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.utils.local_request_guard import require_local_http_request


class GoalCreate(BaseModel):
    goal_id: str | None = None
    title: str
    status: str = "planning"
    steps: list[dict] = Field(default_factory=list)
    permission_envelope: dict = Field(default_factory=lambda: {
        "allowed_capabilities": [],
        "blocked_actions": [],
        "requires_confirmation": [],
    })
    ledger_refs: list[dict] = Field(default_factory=list)


class GoalUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    steps: list[dict] | None = None
    permission_envelope: dict | None = None
    ledger_refs: list[dict] | None = None


def build_goals_router() -> APIRouter:
    router = APIRouter(
        dependencies=[Depends(require_local_http_request)]
    )

    @router.get("/api/goals")
    async def list_goals():
        from src.goals.goal_store import goal_store
        return {"goals": goal_store.list_goals()}

    @router.get("/api/goals/{goal_id}")
    async def get_goal(goal_id: str):
        from src.goals.goal_store import goal_store
        goal = goal_store.get_goal(goal_id)
        if goal is None:
            raise HTTPException(status_code=404, detail="Goal not found")
        return goal

    @router.post("/api/goals", status_code=201)
    async def create_goal(body: GoalCreate):
        from src.goals.goal_store import goal_store
        try:
            created = goal_store.create_goal(body.model_dump())
            return created
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.put("/api/goals/{goal_id}")
    async def update_goal(goal_id: str, body: GoalUpdate):
        from src.goals.goal_store import goal_store
        updates = {
            k: v for k, v in body.model_dump().items() if v is not None
        }
        if not updates:
            raise HTTPException(
                status_code=400, detail="No fields to update"
            )
        try:
            updated = goal_store.update_goal(goal_id, updates)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if updated is None:
            raise HTTPException(status_code=404, detail="Goal not found")
        return updated

    return router
