import logging
from typing import List

from . import prompts
from src.cognition.cognitive_operation_logger import CognitiveOperationLogger
from src.llm import llm_gateway

logger = logging.getLogger(__name__)

MAX_TOKENS = 1000


class DeepSeekBridge:
    """Analysis-only cognitive bridge. No network, no capabilities, no execution."""

    def __init__(self) -> None:
        self._cognitive_log = CognitiveOperationLogger()

    def analyze(self, user_message: str, context: List[dict], suggested_max_tokens: int = 800) -> str:
        started_at = self._cognitive_log.started(
            module_name="deepseek_bridge",
            mode="analysis",
            request_id="deepseek_bridge",
        )
        prompt = prompts.build_analysis_prompt(user_message, context)
        response = ""
        try:
            response = llm_gateway.generate_chat(
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
        finally:
            self._cognitive_log.completed(
                module_name="deepseek_bridge",
                mode="analysis",
                started_at=started_at,
                request_id="deepseek_bridge",
                success=bool(response),
            )
