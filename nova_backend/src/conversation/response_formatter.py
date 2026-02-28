import re
from typing import Dict, Optional


class ResponseFormatter:
    CLARIFICATION_TEMPLATES = {
        "casual": "Would you like a brief answer or a deeper breakdown?",
        "analytical": "Do you want a high-level comparison or implementation detail?",
        "implementation": "Should I stay conceptual, or break this into concrete steps?",
        "brainstorming": "Do you want broad ideas or a narrower direction?",
    }

    DEPTH_PROMPTS = {
        "casual": "If useful, I can break that into a few clear steps.",
        "analytical": "If useful, I can go deeper on tradeoffs and assumptions.",
        "implementation": "If useful, I can map this into an implementation sequence.",
        "brainstorming": "If useful, I can branch this into a few neutral options.",
    }

    @staticmethod
    def format(text: str, mode: str = "casual") -> str:
        clean = (text or "").strip()
        clean = re.sub(r"  +", " ", clean)
        clean = re.sub(r"!+", ".", clean)
        clean = re.sub(r"([.!?])([A-Z])", r"\1 \2", clean)

        for filler in [r"\bwell\b", r"\bso\b", r"\byou see\b"]:
            clean = re.sub(filler, "", clean, flags=re.IGNORECASE)

        clean = ResponseFormatter._tone_shape(clean, mode)
        return re.sub(r"\s{2,}", " ", clean).strip()

    @staticmethod
    def with_conversational_initiative(
        base_text: str,
        mode: str,
        allow_clarification: bool = False,
        allow_branch_suggestion: bool = False,
        allow_depth_prompt: bool = False,
    ) -> str:
        text = ResponseFormatter.format(base_text, mode=mode)
        add_ons = []

        if allow_clarification:
            add_ons.append(ResponseFormatter.CLARIFICATION_TEMPLATES.get(mode, ResponseFormatter.CLARIFICATION_TEMPLATES["casual"]))

        if allow_branch_suggestion:
            add_ons.append("We could approach this in a few ways: direct answer, stepwise plan, or side-by-side comparison.")

        if allow_depth_prompt:
            add_ons.append(ResponseFormatter.DEPTH_PROMPTS.get(mode, ResponseFormatter.DEPTH_PROMPTS["casual"]))

        if add_ons:
            text = f"{text}\n\n" + "\n".join(add_ons[:2])

        return text.strip()

    @staticmethod
    def _tone_shape(text: str, mode: str) -> str:
        if mode == "analytical":
            return text.replace("I think", "The analysis indicates")
        if mode == "implementation" and "\n" not in text and ". " in text:
            return text.replace(". ", ".\n")
        return text
