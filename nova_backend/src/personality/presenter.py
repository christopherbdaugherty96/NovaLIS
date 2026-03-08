from __future__ import annotations

from typing import Iterable

from src.agents.base import AgentOutput


def present_raw_outputs(outputs: Iterable[AgentOutput]) -> str:
    ordered = sorted(list(outputs), key=lambda item: (int(item.tier), str(item.agent_name)))
    lines: list[str] = [
        "Invocation Results",
        "These are raw outputs. I cannot synthesize, prioritize, or resolve contradictions for you.",
        "",
    ]
    for out in ordered:
        lines.append(f"{out.agent_name} (tier {out.tier}) - {out.purpose}")
        lines.append(out.raw_text.strip())
        lines.append("")
    return "\n".join(lines).strip()
