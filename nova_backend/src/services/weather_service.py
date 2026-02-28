# src/services/weather_service.py

import os
import asyncio
from typing import Dict, Optional

from src.governor.exceptions import NetworkMediatorError


class WeatherService:
    """
    WeatherService — Phase-3 Canonical (Visual Crossing)

    Provider: Visual Crossing
    Deterministic, request-on-demand only
    No background updates
    No execution side effects
    Stable normalized output for WeatherSkill

    Phase-4 Admission change:
    - All outbound HTTP routed through NetworkMediator.
    """

    DEFAULT_LOCATION = "Ann Arbor, MI"
    SKILL_NETWORK_CAPABILITY_ID = 48

    def __init__(self, network, location: Optional[str] = None):
        self.network = network
        self.location = location or self.DEFAULT_LOCATION

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
            "include": "current",
            "contentType": "json",
        }

        try:
            # NetworkMediator is synchronous; run in a thread.
            resp = await asyncio.to_thread(
                self.network.request,
                self.SKILL_NETWORK_CAPABILITY_ID,
                "GET",
                url,
                None,  # json_payload
                params,
                None,  # headers
                as_json=True,
                timeout=8.0,
            )
        except NetworkMediatorError as e:
            raise RuntimeError(f"Weather API failed: {e}") from e

        payload = resp.get("data") or {}
        current = payload.get("currentConditions", {}) or {}
        resolved = payload.get("resolvedAddress", "Unknown location")

        return {
            "temperature": current.get("temp", 0),
            "condition": current.get("conditions", "Unknown"),
            "location": resolved.split(",")[0] if resolved else "Unknown",
        }
