import logging
from typing import List

from . import prompts

logger = logging.getLogger(__name__)

MAX_TOKENS = 1000


class DeepSeekBridge:
    """Analysis-only cognitive bridge. No network, no capabilities, no execution."""

    def analyze(self, user_message: str, context: List[dict], suggested_max_tokens: int = 800) -> str:
        del suggested_max_tokens
        prompt = prompts.build_analysis_prompt(user_message, context)

        try:
            import ollama
        except Exception:
            return "I can provide a structured analysis, but the analysis model is currently unavailable."

        try:
            response = ollama.chat(
                model="phi3:mini",
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.2, "num_predict": MAX_TOKENS},
            )
            content = response.get("message", {}).get("content", "")
            return (content or "").strip() or "I can provide a structured analysis, but no analysis output was generated."
        except Exception as error:
            logger.error("Analysis call failed: %s", error)
            return "I can provide a structured analysis, but the analysis model is currently unavailable."
