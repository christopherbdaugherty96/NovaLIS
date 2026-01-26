import os
import httpx
from typing import Dict, Optional


class WeatherService:
    """
    WeatherService — Phase-3 Canonical (Visual Crossing)

    - Provider: Visual Crossing
    - Deterministic, request-on-demand only
    - No background updates
    - No execution side effects
    - Stable normalized output for WeatherSkill
    """

    DEFAULT_LOCATION = "Ann Arbor, MI"

    def __init__(self, location: Optional[str] = None):
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

        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        current = payload.get("currentConditions", {})
        resolved = payload.get("resolvedAddress", "Unknown location")

        return {
            "temperature": current.get("temp", 0),
            "condition": current.get("conditions", "Unknown"),
            "location": resolved.split(",")[0] if resolved else "Unknown",
        }
