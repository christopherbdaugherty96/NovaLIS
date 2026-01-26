from datetime import datetime

# ✅ correct relative imports
from ..base_skill import BaseSkill, SkillResult
from ..services.weather_service import WeatherService


class WeatherSkill(BaseSkill):
    name = "weather"
    description = "Provides the current weather conditions."

    def __init__(self):
        self.service = WeatherService()

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
                    "type": "weather",              # ✅ REQUIRED
                    "data": {                       # ✅ REQUIRED
                        "summary": message,
                        "temperature": round(data["temperature"]),
                        "condition": data["condition"],
                        "location": data["location"],
                    },
                },
                skill=self.name,
            )

        except Exception as e:
            return SkillResult(
                success=False,
                message="Weather is currently unavailable.",
                error=str(e),
                skill=self.name,
            )

    def _format(self, data: dict) -> str:
        timestamp = datetime.now().strftime("%I:%M %p").lstrip("0")
        return (
            f"From the last update at {timestamp}: "
            f"{round(data['temperature'])}°F and {data['condition']} in {data['location']}."
        )
