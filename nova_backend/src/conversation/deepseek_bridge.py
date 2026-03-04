import logging
from typing import List

from . import prompts
from src.llm.llm_gateway import generate_chat

logger = logging.getLogger(__name__)

MAX_TOKENS = 1000


class DeepSeekBridge:
    """Analysis-only cognitive bridge. No network, no capabilities, no execution."""

    def analyze(self, user_message: str, context: List[dict], suggested_max_tokens: int = 800) -> str:
        prompt = prompts.build_analysis_prompt(user_message, context)
        response = generate_chat(
            prompt,
            mode="analysis_only",
            safety_profile="analysis",
            request_id="deepseek_bridge",
            max_tokens=min(MAX_TOKENS, suggested_max_tokens),
            temperature=0.2,
        )
        if response:
            return response
        logger.error("Analysis call failed via centralized gateway.")
        return "I can provide structured analysis, but it is currently unavailable."
