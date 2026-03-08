from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class AgentOutput:
    agent_name: str
    tier: int
    purpose: str
    raw_text: str
    invocation_id: str
    context_hash: str
    generated_at: str


class BaseAgent:
    name = "base"
    tier = 99
    purpose = "base-agent"

    def execute(self, query: str, context: Mapping[str, Any], invocation_id: str, context_hash: str) -> AgentOutput:
        raise NotImplementedError

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
