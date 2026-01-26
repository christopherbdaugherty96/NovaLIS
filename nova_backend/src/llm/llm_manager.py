# backend/llm/llm_manager.py

import requests
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LLMManager:
    """
    Thin wrapper for Ollama LLM integration.
    Responsibilities:
    - Transport only (HTTP)
    - Error handling
    - Stable configuration
    NO routing, NO memory, NO personality logic
    """

    def __init__(
        self,
        model: str = "phi3:mini",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = 30  # seconds
        
        # Connection pooling
        self.session = requests.Session()
        
        # Circuit breaker state
        self.failure_count = 0
        self.circuit_open_until = 0

        # Calibration for Nova's presence-first design
        self.default_options = {
            "temperature": 0.4,      # Calm, not creative
            "num_predict": 256,      # Hard cap on response length
            "num_ctx": 4096,         # ✅ Stable context window
            "top_k": 40,             # Reduce weird outputs
            "repeat_penalty": 1.1,   # Prevent loops
            "stop": ["\n\n", "User:", "Human:"],  # Natural stopping points
        }

    def generate(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """
        Send prompt to LLM and return plain text.

        Rules:
        - No routing logic
        - No memory injection
        - No personality shaping
        - Text in → text out
        """
        
        # -------- Circuit Breaker Check --------
        now = time.time()
        if now < self.circuit_open_until:
            logger.warning(f"Circuit breaker open. Skipping request until {self.circuit_open_until}")
            return None

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": self.default_options,
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            result = response.json()
            
            # -------- Reset failure count on success --------
            self.failure_count = 0
            
            return result.get("response", "").strip()

        except requests.exceptions.Timeout:
            logger.warning(f"LLM request timed out after {self.timeout}s")
            self._record_failure()
            
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running?")
            self._record_failure()
            
        except Exception as e:
            logger.error(f"LLM error: {e}")
            self._record_failure()

        return None

    def _record_failure(self):
        """
        Track failures and open circuit after 3 consecutive failures.
        """
        self.failure_count += 1
        if self.failure_count >= 3:
            self.circuit_open_until = time.time() + 30  # 30-second cooldown
            logger.warning(f"Circuit breaker opened. Will retry after 30 seconds.")
            self.failure_count = 0

    def health_check(self) -> bool:
        """
        Verify Ollama is running and the model is available.
        Uses partial match to allow different quantizations.
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(self.model in m.get("name", "") for m in models)
        except Exception:
            pass

        return False


# Singleton instance (safe for Nova's current scale)
llm_manager = LLMManager()