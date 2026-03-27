# src/skills/weather.py

from datetime import datetime
import logging
import re

from src.base_skill import BaseSkill, SkillResult
from src.services.weather_service import WeatherService
from src.governor.network_mediator import NetworkMediator

log = logging.getLogger("nova.skills.weather")


class WeatherSkill(BaseSkill):
    name = "weather"
    description = "Provides the current weather conditions."

    _TIME_HINTS = (
        "outside",
        "today",
        "tomorrow",
        "right now",
        "this morning",
        "this afternoon",
        "this evening",
        "tonight",
        "later",
    )

    def __init__(self, network: NetworkMediator | None = None):
        self.service = WeatherService(network=network)

    def can_handle(self, text: str) -> bool:
        query = str(text or "").strip().lower()
        if not query:
            return False
        if "weather" in query or "forecast" in query:
            return True
        if ("temperature" in query or re.search(r"\btemp\b", query)) and any(
            hint in query for hint in self._TIME_HINTS
        ):
            return True
        if any(term in query for term in ("rain", "snow", "umbrella", "conditions")) and any(
            hint in query for hint in self._TIME_HINTS
        ):
            return True
        return False

    async def handle(self, text: str) -> SkillResult:
        try:
            data = await self.service.get_current_weather()
            message = self._format(data)
            timestamp = datetime.now().strftime("%I:%M %p").lstrip("0")
            alerts = list(data.get("alerts") or [])
            forecast = str(data.get("forecast") or "").strip()

            return SkillResult(
                success=True,
                message=message,
                data=data,
                widget_data={
                    "type": "weather",
                    "data": {
                        "summary": message,
                        "temperature": round(data["temperature"]),
                        "condition": data["condition"],
                        "location": data["location"],
                        "forecast": forecast,
                        "alerts": alerts,
                        "updated_at": timestamp,
                        "status": "ok",
                        "connected": True,
                        "provider": "Visual Crossing",
                        "setup_hint": "",
                    },
                },
                skill=self.name,
            )

        except Exception as e:
            log.debug(f"Weather failure: {e}")
            detail = str(e or "").strip()
            if "WEATHER_API_KEY" in detail:
                message = "Weather is available, but no provider key is configured yet."
                status = "not_configured"
                connected = False
                setup_hint = "Add WEATHER_API_KEY to enable live weather."
            else:
                message = "Weather is unavailable right now."
                status = "unavailable"
                connected = False
                setup_hint = ""
            timestamp = datetime.now().strftime("%I:%M %p").lstrip("0")
            return SkillResult(
                success=True,
                message=message,
                data={
                    "connected": connected,
                    "status": status,
                    "setup_hint": setup_hint,
                },
                widget_data={
                    "type": "weather",
                    "data": {
                        "summary": message,
                        "forecast": "",
                        "alerts": [],
                        "updated_at": timestamp,
                        "status": status,
                        "connected": connected,
                        "provider": "Visual Crossing",
                        "setup_hint": setup_hint,
                    },
                },
                skill=self.name,
            )

    def _format(self, data: dict) -> str:
        timestamp = datetime.now().strftime("%I:%M %p").lstrip("0")
        base = (
            f"From the last update at {timestamp}: "
            f"{round(data['temperature'])} degrees F and {data['condition']} in {data['location']}."
        )
        alerts = list(data.get("alerts") or [])
        if alerts:
            return f"{base} Alert active: {alerts[0]}"
        return base
