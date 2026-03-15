from __future__ import annotations

from typing import Iterable

from src.agents.base import AgentOutput


def present_raw_outputs(outputs: Iterable[AgentOutput]) -> str:
    ordered = sorted(list(outputs), key=lambda item: (int(item.tier), str(item.agent_name)))
    lines: list[str] = [
        "Invocation Results",
        "Orthogonal Review",
        "These are independent, non-authorizing analysis tracks.",
        "Nova is not synthesizing, prioritizing, or resolving contradictions for you in this mode.",
        "",
    ]
    for index, out in enumerate(ordered, start=1):
        lines.append(f"{index}. {out.agent_name} | tier {out.tier} | {out.purpose}")
        lines.append(out.raw_text.strip() or "No output produced.")
        lines.append("")
    return "\n".join(lines).strip()
