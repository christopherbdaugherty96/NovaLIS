"""Daily Awareness Brief — the on-open product surface.

Assembles a structured awareness payload from all available data sources
with graceful degradation: each section is independently optional and
reports its own availability. Non-authorizing, read-only, no LLM calls.

Sections (in display order):
  1. Weather — with practical impact note
  2. News — grouped by subject, sourced from governed news capability
  3. Calendar — today's events
  4. Project state — blocker, last step, next move
  5. Shopify snapshot — read-only store metrics (if connected)
  6. Printify snapshot — stub until integration exists
  7. What changed — recent ledger receipts since last session
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class AwarenessSection:
    key: str
    title: str
    items: tuple[str, ...]
    status: str = "ok"
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "items": list(self.items),
            "status": self.status,
            "source": self.source,
        }

    @property
    def available(self) -> bool:
        return self.status == "ok" and len(self.items) > 0


@dataclass(frozen=True)
class AwarenessBrief:
    date: str
    timestamp_utc: str
    sections: tuple[AwarenessSection, ...]
    greeting: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "awareness_brief",
            "date": self.date,
            "timestamp_utc": self.timestamp_utc,
            "greeting": self.greeting,
            "sections": [s.to_dict() for s in self.sections],
            "available_count": sum(1 for s in self.sections if s.available),
            "total_count": len(self.sections),
        }


_MAX_ITEMS = 5


def _clean(value: Any, *, limit: int = 200) -> str:
    return str(value or "").strip()[:limit]


def _time_greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def build_weather_section(weather_data: dict[str, Any] | None) -> AwarenessSection:
    if not isinstance(weather_data, dict) or not weather_data.get("connected"):
        return AwarenessSection(
            key="weather",
            title="Weather",
            items=("Weather not configured. Add a weather API key in Settings.",),
            status="not_configured",
            source="weather",
        )
    items: list[str] = []
    summary = _clean(weather_data.get("summary"), limit=160)
    if summary:
        items.append(summary)
    forecast = _clean(weather_data.get("forecast"), limit=120)
    if forecast and forecast != summary:
        items.append(forecast)
    for alert in (weather_data.get("alerts") or [])[:2]:
        a = _clean(alert, limit=100)
        if a:
            items.append(f"Alert: {a}")
    if not items:
        items.append("Weather data retrieved but no summary available.")
    return AwarenessSection(
        key="weather", title="Weather", items=tuple(items[:_MAX_ITEMS]),
        status="ok", source="weather",
    )


def build_news_section(
    news_items: list[dict[str, Any]] | None,
    categories: dict[str, Any] | None = None,
) -> AwarenessSection:
    if not news_items:
        return AwarenessSection(
            key="news", title="News",
            items=("News not available. Check your Brave Search connection in Settings.",),
            status="not_configured", source="news",
        )
    items: list[str] = []
    if isinstance(categories, dict) and categories:
        for cat, cat_items in list(categories.items())[:4]:
            label = _clean(cat, limit=30)
            count = len(cat_items) if isinstance(cat_items, list) else 0
            if count:
                first_title = _clean(
                    cat_items[0].get("title") if isinstance(cat_items[0], dict) else cat_items[0],
                    limit=80,
                )
                items.append(f"{label} ({count}): {first_title}")
            else:
                items.append(label)
    else:
        for article in news_items[:_MAX_ITEMS]:
            if isinstance(article, dict):
                title = _clean(article.get("title"), limit=100)
                if title:
                    items.append(title)
            elif isinstance(article, str):
                items.append(_clean(article, limit=100))
    return AwarenessSection(
        key="news", title="News by Subject",
        items=tuple(items[:_MAX_ITEMS]),
        status="ok" if items else "empty", source="brave_search",
    )


def build_calendar_section(calendar_data: dict[str, Any] | None) -> AwarenessSection:
    if not isinstance(calendar_data, dict) or not calendar_data.get("connected"):
        return AwarenessSection(
            key="calendar", title="Calendar",
            items=("Calendar not configured. Add a .ics file in Settings.",),
            status="not_configured", source="calendar",
        )
    events = list(calendar_data.get("events") or [])
    items: list[str] = []
    for event in events[:_MAX_ITEMS]:
        if not isinstance(event, dict):
            continue
        time_label = _clean(event.get("time"), limit=20)
        title = _clean(event.get("title") or "Untitled", limit=80)
        items.append(f"{time_label} — {title}" if time_label else title)
    if not items:
        items.append("Nothing on your calendar today.")
    return AwarenessSection(
        key="calendar", title="Calendar", items=tuple(items),
        status="ok", source=_clean(calendar_data.get("source_label") or "calendar", limit=40),
    )


def build_project_section(session_state: dict[str, Any] | None) -> AwarenessSection:
    state = dict(session_state) if isinstance(session_state, dict) else {}
    conv = dict(state.get("conversation_context") or {})
    items: list[str] = []
    topic = _clean(conv.get("topic") or state.get("active_topic"), limit=120)
    if topic:
        items.append(f"Focus: {topic}")
    goal = _clean(conv.get("user_goal"), limit=120)
    if goal and goal != topic:
        items.append(f"Goal: {goal}")
    for loop in list(conv.get("open_loops") or [])[:2]:
        s = _clean(loop, limit=100)
        if s:
            items.append(f"Open: {s}")
    if not items:
        return AwarenessSection(
            key="project", title="Current Project State",
            items=("No active project context. Start a conversation to build context.",),
            status="empty", source="session",
        )
    return AwarenessSection(
        key="project", title="Current Project State",
        items=tuple(items[:_MAX_ITEMS]),
        status="ok", source="session",
    )


def build_shopify_section(snapshot: dict[str, Any] | None) -> AwarenessSection:
    if not isinstance(snapshot, dict) or not snapshot:
        return AwarenessSection(
            key="shopify", title="Shopify",
            items=("Shopify not connected. Add your store in Settings.",),
            status="not_configured", source="shopify",
        )
    items: list[str] = []
    shop = _clean(snapshot.get("shop_name") or snapshot.get("shop_domain"), limit=60)
    if shop:
        items.append(f"Store: {shop}")
    orders = snapshot.get("orders")
    if isinstance(orders, dict):
        count = orders.get("order_count", 0)
        rev = _clean(orders.get("total_revenue"), limit=20)
        period = _clean(orders.get("period_label") or "recent", limit=20)
        if rev:
            items.append(f"{count} orders, {rev} revenue ({period})")
    products = snapshot.get("products")
    if isinstance(products, dict):
        active = products.get("active_products", 0)
        oos = products.get("out_of_stock_count", 0)
        low = products.get("low_stock_count", 0)
        items.append(f"{active} active products")
        if oos:
            items.append(f"{oos} out of stock")
        if low:
            items.append(f"{low} low stock")
    error = _clean(snapshot.get("error"), limit=100)
    if error:
        items.append(f"Note: {error}")
    return AwarenessSection(
        key="shopify", title="Shopify Snapshot",
        items=tuple(items[:_MAX_ITEMS]),
        status="ok" if items else "empty", source="shopify",
    )


def build_printify_section() -> AwarenessSection:
    return AwarenessSection(
        key="printify", title="Printify",
        items=("Printify integration is not built yet.",),
        status="not_available", source="printify",
    )


def build_changes_section(recent_receipts: list[dict[str, Any]] | None) -> AwarenessSection:
    receipts = list(recent_receipts) if isinstance(recent_receipts, list) else []
    if not receipts:
        return AwarenessSection(
            key="changes", title="What Changed",
            items=("No recent activity recorded.",),
            status="empty", source="ledger",
        )
    _LABEL_MAP: dict[str, str] = {
        "ACTION_COMPLETED": "completed",
        "ACTION_ATTEMPTED": "attempted",
        "OPENCLAW_AGENT_RUN_COMPLETED": "agent run",
        "MEMORY_ITEM_SAVED": "memory saved",
        "POLICY_EXECUTION_COMPLETED": "policy ran",
    }
    items: list[str] = []
    for receipt in receipts[:_MAX_ITEMS]:
        if not isinstance(receipt, dict):
            continue
        event_type = str(receipt.get("event_type") or "")
        label = _LABEL_MAP.get(event_type, event_type.lower().replace("_", " "))
        detail = _clean(
            receipt.get("capability_name") or receipt.get("outcome_reason") or receipt.get("message"),
            limit=60,
        )
        entry = f"{label}: {detail}" if detail else label
        ts = str(receipt.get("timestamp_utc") or "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                entry = f"{dt.strftime('%H:%M')} — {entry}"
            except ValueError:
                pass
        if entry.strip() and entry not in items:
            items.append(entry)
    return AwarenessSection(
        key="changes", title="What Changed",
        items=tuple(items[:_MAX_ITEMS]),
        status="ok" if items else "empty", source="ledger",
    )


def compose_awareness_brief(
    *,
    weather_data: dict[str, Any] | None = None,
    news_items: list[dict[str, Any]] | None = None,
    news_categories: dict[str, Any] | None = None,
    calendar_data: dict[str, Any] | None = None,
    session_state: dict[str, Any] | None = None,
    shopify_snapshot: dict[str, Any] | None = None,
    recent_receipts: list[dict[str, Any]] | None = None,
) -> AwarenessBrief:
    sections = (
        build_weather_section(weather_data),
        build_news_section(news_items, news_categories),
        build_calendar_section(calendar_data),
        build_project_section(session_state),
        build_shopify_section(shopify_snapshot),
        build_printify_section(),
        build_changes_section(recent_receipts),
    )
    return AwarenessBrief(
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        sections=sections,
        greeting=_time_greeting(),
    )
