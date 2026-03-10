# src/services/weather_service.py

import os
import asyncio
import re
from typing import Dict, Optional

from src.governor.network_mediator import NetworkMediator
from src.governor.exceptions import NetworkMediatorError


NETWORK_CAPABILITY_ID = 55
WEATHER_TIMEOUT_SECONDS = 8.0
WEATHER_MAX_RETRIES = 1
WEATHER_RETRY_BACKOFF_SECONDS = 0.35


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

    def _build_request_url(self) -> str:
        normalized_location = self._clean_text(self.location, limit=120) or self.DEFAULT_LOCATION
        encoded_location = normalized_location.replace("%", "").replace(" ", "%20")
        return (
            "https://weather.visualcrossing.com/"
            "VisualCrossingWebServices/rest/services/timeline/"
            f"{encoded_location}/today"
        )

    async def _request_weather_payload(self, url: str, params: dict) -> dict:
        last_error: Exception | None = None

        for attempt in range(WEATHER_MAX_RETRIES + 1):
            try:
                resp = await asyncio.to_thread(
                    self.network.request,
                    capability_id=NETWORK_CAPABILITY_ID,
                    method="GET",
                    url=url,
                    json_payload=None,
                    params=params,
                    headers=None,
                    as_json=True,
                    timeout=WEATHER_TIMEOUT_SECONDS,
                )

                status_code = int(resp.get("status_code") or 0)
                if status_code and status_code != 200:
                    raise RuntimeError(f"Unexpected weather status: {status_code}")

                payload = resp.get("data") or {}
                if not isinstance(payload, dict):
                    raise RuntimeError("Weather response payload was not a JSON object.")
                return payload

            except (NetworkMediatorError, RuntimeError) as error:
                last_error = error
                if attempt < WEATHER_MAX_RETRIES:
                    await asyncio.sleep(WEATHER_RETRY_BACKOFF_SECONDS * (attempt + 1))
                    continue
                break

        raise RuntimeError("Weather API failed.") from last_error

    async def get_current_weather(self) -> Dict[str, str]:
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            raise RuntimeError("Missing WEATHER_API_KEY")

        url = self._build_request_url()

        params = {
            "key": api_key,
            "unitGroup": "us",
            "include": "current,days,alerts",
            "contentType": "json",
        }

        payload = await self._request_weather_payload(url, params)
        current = payload.get("currentConditions", {}) or {}
        resolved = self._clean_text(payload.get("resolvedAddress", "Unknown location"), limit=80)
        forecast = self._build_forecast(payload)
        alerts = self._extract_alerts(payload)

        raw_temp = current.get("temp", 0)
        try:
            temperature = float(raw_temp)
        except Exception:
            temperature = 0.0

        condition = self._clean_text(current.get("conditions", "Unknown"), limit=80) or "Unknown"
        location = self._clean_text((resolved.split(",")[0] if resolved else ""), limit=48) or "Unknown"

        return {
            "temperature": temperature,
            "condition": condition,
            "location": location,
            "forecast": forecast,
            "alerts": alerts,
        }
