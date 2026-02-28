import logging
import os
from typing import List

from . import prompts

logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MAX_TOKENS = 1000
TIMEOUT = 15
DEEP_THOUGHT_CAPABILITY_ID = 48


class DeepSeekBridge:
    def __init__(self, network):
        self.network = network

    def process(self, user_message: str, context: List[dict], suggested_max_tokens: int = 800) -> str:
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            return "I'm sorry, the deep analysis service is temporarily unavailable."

        prompt = prompts.build_analysis_prompt(user_message, context)
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": min(suggested_max_tokens, MAX_TOKENS),
            "temperature": 0.3,
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        try:
            response = self.network.request(
                capability_id=DEEP_THOUGHT_CAPABILITY_ID,
                method="POST",
                url=DEEPSEEK_API_URL,
                json_payload=payload,
                headers=headers,
                as_json=True,
                timeout=TIMEOUT,
            )
            data = response.get("data") or {}
            return data.get("choices", [{}])[0].get("message", {}).get(
                "content", "I'm sorry, the deep analysis service is temporarily unavailable."
            )
        except Exception as error:
            logger.error("DeepSeek API call failed: %s", error)
            return "I'm sorry, the deep analysis service is temporarily unavailable."
