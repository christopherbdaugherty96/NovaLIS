"""
System Skill — Phase 3
Provides basic system status, uptime, and local time/date.
Safe, deterministic, internal-only.
"""

from datetime import datetime
import time
import platform

from ..base_skill import BaseSkill, SkillResult


class SystemSkill(BaseSkill):
    name = "system"
    start_time = time.time()

    # ----------------------------
    # Can this skill handle input?
    # ----------------------------
    def can_handle(self, query: str) -> bool:
        tokens = query.lower().split()
        return any(token in {
            "system",
            "status",
            "health",
            "uptime",
            "time",
            "date"
        } for token in tokens)

    # ----------------------------
    # Handle the request
    # ----------------------------
    async def handle(self, query: str) -> SkillResult:
        q = query.lower()
        uptime_seconds = int(time.time() - self.start_time)

        # Time / date requests
        if "time" in q:
            now = datetime.now().strftime("%I:%M %p").lstrip("0")
            return SkillResult(
                success=True,
                message=f"It is {now}.",
                data={"time": now},
                skill=self.name,
            )

        if "date" in q:
            today = datetime.now().strftime("%A, %B %d, %Y")
            return SkillResult(
                success=True,
                message=f"Today is {today}.",
                data={"date": today},
                skill=self.name,
            )

        # System / status requests
        data = {
            "platform": platform.system(),
            "uptime_seconds": uptime_seconds,
            "status": "running",
        }

        message = (
            "System status is normal. "
            f"Uptime: {uptime_seconds} seconds."
        )

        return SkillResult(
            success=True,
            message=message,
            data=data,
            skill=self.name,
        )
