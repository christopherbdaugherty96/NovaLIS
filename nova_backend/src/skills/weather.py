# src/skills/weather.py

from datetime import datetime
import logging

from src.base_skill import BaseSkill, SkillResult
from src.services.weather_service import WeatherService
from src.governor.network_mediator import NetworkMediator

log = logging.getLogger("nova.skills.weather")


class WeatherSkill(BaseSkill):
    name = "weather"
    description = "Provides the current weather conditions."

    def __init__(self, network: NetworkMediator | None = None):
        self.service = WeatherService(network=network)

    def can_handle(self, text: str) -> bool:
        return "weather" in text.lower()

    async def handle(self, text: str) -> SkillResult:
        try:
            data = await self.service.get_current_weather()
            message = self._format(data)

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
                    },
                },
                skill=self.name,
            )

        except Exception as e:
            log.debug(f"Weather failure: {e}")
            return SkillResult(
                success=False,
                message="Weather is currently unavailable.",
                skill=self.name,
            )

    def _format(self, data: dict) -> str:
        timestamp = datetime.now().strftime("%I:%M %p").lstrip("0")
        return (
            f"From the last update at {timestamp}: "
            f"{round(data['temperature'])} degrees F and {data['condition']} in {data['location']}."
        )
