# src/api/trust_api.py
"""
Trust receipt API — exposes recent governed action receipts.

GET /api/trust/receipts          — last N receipt-worthy ledger events
GET /api/trust/receipts/summary  — quick summary for dashboard badge

Both endpoints are local-only (loopback guard applied at the router level via
_LOCAL_ONLY_API_PREFIXES in local_request_guard.py).
"""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, Query

from src.utils.local_request_guard import require_local_http_request


def build_trust_router() -> APIRouter:
    router = APIRouter(dependencies=[Depends(require_local_http_request)])

    @router.get("/api/trust/receipts")
    async def trust_receipts(limit: int = Query(default=20, ge=1, le=100)):
        from src.trust.receipt_store import get_recent_receipts
        return {"receipts": await asyncio.to_thread(get_recent_receipts, limit=limit)}

    @router.get("/api/trust/receipts/summary")
    async def trust_receipts_summary():
        from src.trust.receipt_store import get_receipt_summary
        return await asyncio.to_thread(get_receipt_summary)

    return router
