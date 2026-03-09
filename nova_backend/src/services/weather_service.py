# src/services/weather_service.py

import os
import asyncio
import re
from typing import Dict, Optional

from src.governor.network_mediator import NetworkMediator
from src.governor.exceptions import NetworkMediatorError


NETWORK_CAPABILITY_ID = 16


class WeatherService:
    """
    WeatherService — Phase-3 Canonical (Visual Crossing)

    Provider: Visual Crossing
    Deterministic, request-on-demand only
    No background updates
    No execution side effects
    Stable normalized output for WeatherSkill

    Phase-4 Admission change:
    - All outbound HTTP routed through NetworkMediator (no direct httpx).
    """

    DEFAULT_LOCATION = "Ann Arbor, MI"

    def _clean_text(self, value: object, *, limit: int = 160) -> str:
        text = str(value or "")
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > limit:
            text = text[: limit - 3].rstrip() + "..."
        return text

    def _format_temp(self, value: object) -> str:
        try:
            return f"{round(float(value))}F"
        except Exception:
            return "n/a"

    def _build_forecast(self, payload: dict) -> str:
        days = payload.get("days") or []
        if not isinstance(days, list) or not days:
            return ""

        segments: list[str] = []
        today = days[0] if isinstance(days[0], dict) else {}
        tomorrow = days[1] if len(days) > 1 and isinstance(days[1], dict) else {}

        if today:
            segments.append(
                "Today: "
                f"{self._format_temp(today.get('tempmax'))}/{self._format_temp(today.get('tempmin'))}, "
                f"{self._clean_text(today.get('conditions') or 'Unknown conditions', limit=70)}"
            )
        if tomorrow:
            segments.append(
                "Tomorrow: "
                f"{self._format_temp(tomorrow.get('tempmax'))}/{self._format_temp(tomorrow.get('tempmin'))}, "
                f"{self._clean_text(tomorrow.get('conditions') or 'Unknown conditions', limit=70)}"
            )
        return " | ".join(segments[:2])

    def _extract_alerts(self, payload: dict) -> list[str]:
        raw_alerts = payload.get("alerts") or []
        if not isinstance(raw_alerts, list):
            return []

        alerts: list[str] = []
        for alert in raw_alerts:
            if isinstance(alert, dict):
                msg = (
                    alert.get("headline")
                    or alert.get("event")
                    or alert.get("description")
                    or alert.get("title")
                    or ""
                )
            else:
                msg = str(alert or "")
            clean = self._clean_text(msg, limit=140)
            if not clean or clean in alerts:
                continue
            alerts.append(clean)
            if len(alerts) >= 3:
                break
        return alerts

    def __init__(self, location: Optional[str] = None, network: Optional[NetworkMediator] = None):
        self.location = location or self.DEFAULT_LOCATION
        self.network = network or NetworkMediator()

    async def get_current_weather(self) -> Dict[str, str]:
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            raise RuntimeError("Missing WEATHER_API_KEY")

        url = (
            "https://weather.visualcrossing.com/"
            "VisualCrossingWebServices/rest/services/timeline/"
            f"{self.location}/today"
        )

        params = {
            "key": api_key,
            "unitGroup": "us",
            "include": "current,days,alerts",
            "contentType": "json",
        }

        try:
            # NetworkMediator is synchronous; run in a thread.
            resp = await asyncio.to_thread(
                self.network.request,
                NETWORK_CAPABILITY_ID,
                "GET",
                url,
                None,  # json_payload
                params,
                None,  # headers
                as_json=True,
                timeout=8.0,  # keep prior behavior close to httpx timeout
            )
        except NetworkMediatorError as e:
            raise RuntimeError(f"Weather API failed: {e}") from e

        payload = resp.get("data") or {}
        current = payload.get("currentConditions", {}) or {}
        resolved = payload.get("resolvedAddress", "Unknown location")
        forecast = self._build_forecast(payload)
        alerts = self._extract_alerts(payload)

        return {
            "temperature": current.get("temp", 0),
            "condition": current.get("conditions", "Unknown"),
            "location": resolved.split(",")[0] if resolved else "Unknown",
            "forecast": forecast,
            "alerts": alerts,
        }
