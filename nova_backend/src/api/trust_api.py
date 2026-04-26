# src/api/trust_api.py
"""
Trust receipt API — exposes recent governed action receipts.

GET /api/trust/receipts          — last N receipt-worthy ledger events
GET /api/trust/receipts/summary  — quick summary for dashboard badge
"""
from __future__ import annotations

from fastapi import APIRouter, Query


def build_trust_router() -> APIRouter:
    router = APIRouter()

    @router.get("/api/trust/receipts")
    async def trust_receipts(limit: int = Query(default=20, ge=1, le=100)):
        from src.trust.receipt_store import get_recent_receipts
        return {"receipts": get_recent_receipts(limit=limit)}

    @router.get("/api/trust/receipts/summary")
    async def trust_receipts_summary():
        from src.trust.receipt_store import get_receipt_summary
        return get_receipt_summary()

    return router
