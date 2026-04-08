# src/llm/llm_manager.py

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

from src.ledger.writer import LedgerWriter
from src.governor.exceptions import LedgerWriteFailed
from src.llm.model_network_mediator import ModelNetworkMediator, ModelNetworkMediatorError
from src.nova_config import OLLAMA_MODEL, OLLAMA_FALLBACK_MODEL, OLLAMA_URL
from .system_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Paths for version lock
MODEL_HASH_FILE = Path(__file__).resolve().parents[1] / "models" / "current_model_hash.txt"
WRAPPER_PATH = Path(__file__).parent / "inference_wrapper.py"


def compute_model_hash(
    model_digest: str,
    system_prompt: str,
    wrapper_code: str,
    params: Dict[str, Any]
) -> str:
    """Composite hash of all model‑influencing components."""
    blob = json.dumps(
        {
            "model_digest": model_digest,
            "system_prompt": system_prompt,
            "wrapper": wrapper_code,
            "params": params,
        },
        sort_keys=True,
    )
    return hashlib.sha256(blob.encode()).hexdigest()


class LLMManager:
    """
    Ollama LLM integration with constitutional version locking.
    - Thin wrapper around Ollama HTTP API
    - Circuit breaker for reliability
    - Model version hash to detect silent changes
    - Blocks inference on version mismatch
    """

    FALLBACK_THRESHOLD = 5

    def __init__(
        self,
        model: str | None = None,
        fallback_model: str | None = None,
        base_url: str | None = None,
    ):
        self.model = str(model or OLLAMA_MODEL or "gemma4:e4b").strip()
        self.fallback_model = str(fallback_model or OLLAMA_FALLBACK_MODEL or "").strip()
        self.base_url = str(base_url or OLLAMA_URL or "http://localhost:11434").strip()
        self.timeout = 30
        self.system_prompt = SYSTEM_PROMPT
        self._network = ModelNetworkMediator()

        # Circuit breaker state
        self.failure_count = 0
        self.circuit_open_until = 0
        self._using_fallback = False

        # Stable inference parameters (these become part of the version hash)
        self.default_options = {
            "temperature": 0.4,
            "num_predict": 256,
            "num_ctx": 4096,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "stop": ["\n\n", "User:", "Human:"],
        }

        # Version lock state
        self.inference_blocked = False
        self._check_model_version()

    @property
    def active_model(self) -> str:
        if self._using_fallback and self.fallback_model:
            return self.fallback_model
        return self.model

    def try_recover_primary(self) -> bool:
        """Attempt to switch back to the primary model after fallback."""
        if not self._using_fallback:
            return True
        try:
            response = self._network.request_json(
                method="GET",
                url=f"{self.base_url.rstrip('/')}/api/tags",
                timeout=5,
            )
            models = response.data.get("models", [])
            if any(self.model in m.get("name", "") for m in models):
                self._using_fallback = False
                self.failure_count = 0
                logger.info("Recovered to primary model %s.", self.model)
                return True
        except Exception:
            pass
        return False

    def status_snapshot(self) -> dict:
        """Return current model status for diagnostics."""
        return {
            "primary_model": self.model,
            "fallback_model": self.fallback_model or None,
            "active_model": self.active_model,
            "using_fallback": self._using_fallback,
            "inference_blocked": self.inference_blocked,
            "failure_count": self.failure_count,
            "circuit_open": time.time() < self.circuit_open_until,
        }

    # ----- Version lock helpers -------------------------------------------------

    def _get_model_digest(self) -> Optional[str]:
        """Query Ollama for the current model's digest (SHA256 of the blob)."""
        try:
            response = self._network.request_json(
                method="POST",
                url=f"{self.base_url.rstrip('/')}/api/show",
                json_payload={"model": self.model},
                timeout=5,
            )
            data = response.data
            digest = data.get("digest")
            if digest:
                return digest
            logger.info("Ollama /api/show omitted digest for model %s; falling back to /api/tags.", self.model)
            return self._get_model_digest_from_tags()
        except Exception as e:
            logger.warning(f"Could not fetch model digest: {e}")
            return None

    def _get_model_digest_from_tags(self) -> Optional[str]:
        """Fallback digest lookup for Ollama versions that omit digest from /api/show."""
        try:
            response = self._network.request_json(
                method="GET",
                url=f"{self.base_url.rstrip('/')}/api/tags",
                timeout=5,
            )
        except Exception as error:
            logger.warning("Could not fetch model digest from tags: %s", error)
            return None

        models = response.data.get("models", [])
        for model_entry in models:
            if model_entry.get("name") == self.model:
                digest = model_entry.get("digest")
                if digest:
                    return digest
        return None

    def _compute_current_hash(self) -> str:
        """Compute hash based on current configuration."""
        model_digest = self._get_model_digest()
        if model_digest is None:
            model_digest = "fetch_failed"
            logger.warning("Using fallback digest 'fetch_failed' – inference will block until confirmed.")
        with open(WRAPPER_PATH, "r", encoding="utf-8") as f:
            wrapper_code = f.read()
        return compute_model_hash(
            model_digest,
            self.system_prompt,
            wrapper_code,
            self.default_options,
        )

    def _block_inference(self):
        """Prevent any generation for this session."""
        self.inference_blocked = True
        logger.warning("Model inference blocked due to version mismatch.")

    def _log_model_updated(
        self,
        previous_hash: Optional[str],
        new_hash: str,
        user_confirmed: bool,
    ) -> None:
        """Write MODEL_UPDATED event to ledger."""
        writer = LedgerWriter()
        params_hash = hashlib.sha256(
            json.dumps(self.default_options, sort_keys=True).encode()
        ).hexdigest()
        system_prompt_hash = hashlib.sha256(self.system_prompt.encode()).hexdigest()
        with open(WRAPPER_PATH, "r", encoding="utf-8") as f:
            wrapper_code = f.read()
        wrapper_hash = hashlib.sha256(wrapper_code.encode()).hexdigest()
        model_digest = self._get_model_digest() or "unknown"

        metadata = {
            "model_name": self.model,
            "previous_hash": previous_hash,
            "new_hash": new_hash,
            "model_digest": model_digest,
            "system_prompt_hash": system_prompt_hash,
            "wrapper_hash": wrapper_hash,
            "parameter_hash": params_hash,
            "user_confirmed": user_confirmed,
            "confirmation_timestamp": None,
        }
        try:
            writer.log_event("MODEL_UPDATED", metadata)
        except LedgerWriteFailed:
            # Even if ledger fails, we must still block inference
            self._block_inference()
            raise

    def _check_model_version(self):
        """Compare stored hash with current; block if mismatch or first run."""
        computed = self._compute_current_hash()

        if MODEL_HASH_FILE.exists():
            stored = MODEL_HASH_FILE.read_text().strip()
            if stored == computed:
                logger.info("Model version OK.")
                return
            else:
                logger.warning("Model version mismatch. Blocking inference.")
                self._block_inference()
                self._log_model_updated(stored, computed, user_confirmed=False)
        else:
            # First run – block and require confirmation
            logger.info("First model run – blocking inference until confirmed.")
            self._block_inference()
            self._log_model_updated(None, computed, user_confirmed=False)

    def confirm_model_update(self):
        """
        Called after user explicitly confirms a model update.
        Writes the new hash and unblocks inference.
        """
        if not self.inference_blocked:
            return

        # Ensure the models/ directory exists
        MODEL_HASH_FILE.parent.mkdir(parents=True, exist_ok=True)

        computed = self._compute_current_hash()
        previous = None
        if MODEL_HASH_FILE.exists():
            previous = MODEL_HASH_FILE.read_text().strip()
        MODEL_HASH_FILE.write_text(computed)
        self.inference_blocked = False
        self._log_model_updated(previous, computed, user_confirmed=True)
        logger.info("Model update confirmed. Inference unblocked.")

    # ----- Existing functionality (circuit breaker, generate) -----------------

    def _record_failure(self):
        self.failure_count += 1
        if not self._using_fallback and self.fallback_model and self.failure_count >= self.FALLBACK_THRESHOLD:
            self._using_fallback = True
            self.failure_count = 0
            self.circuit_open_until = 0
            logger.warning("Switched to fallback model %s after %d failures.", self.fallback_model, self.FALLBACK_THRESHOLD)
            return
        if self.failure_count >= 3:
            self.circuit_open_until = time.time() + 30
            logger.warning("Circuit breaker opened. Will retry after 30 seconds.")
            self.failure_count = 0

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Send prompt to LLM and return plain text.
        Honors circuit breaker and model version lock.
        """
        if self.inference_blocked:
            logger.error("Generate called while model is blocked.")
            return None

        # Circuit breaker
        now = time.time()
        if now < self.circuit_open_until:
            logger.warning("Circuit breaker open. Skipping request.")
            return None

        # Use the provided system prompt or the default
        system = system_prompt or self.system_prompt

        options = dict(self.default_options)
        if temperature is not None:
            options["temperature"] = float(temperature)
        if max_tokens is not None:
            options["num_predict"] = int(max_tokens)
        request_timeout = float(timeout) if timeout is not None else float(self.timeout)

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._network.request_json(
                method="POST",
                url=f"{self.base_url.rstrip('/')}/api/chat",
                json_payload={
                    "model": self.active_model,
                    "messages": messages,
                    "stream": False,
                    "options": options,
                },
                timeout=request_timeout,
                request_id=request_id,
                session_id=session_id,
            )
            result = ((response.data.get("message") or {}).get("content") or "").strip() or None
            # Success – reset failure count
            self.failure_count = 0
            return result

        except ModelNetworkMediatorError as error:
            logger.error("Model network call failed: %s", error)
            self._record_failure()
        except Exception as e:
            logger.error(f"LLM error: {e}")
            self._record_failure()

        return None

    def health_check(self) -> bool:
        """Verify Ollama is running and the model is available."""
        try:
            response = self._network.request_json(
                method="GET",
                url=f"{self.base_url.rstrip('/')}/api/tags",
                timeout=5,
            )
            if response.status_code == 200:
                models = response.data.get("models", [])
                return any(self.active_model in m.get("name", "") for m in models)
        except Exception:
            pass
        return False


# Singleton instance — reads OLLAMA_MODEL / OLLAMA_FALLBACK_MODEL / OLLAMA_URL from nova_config
llm_manager = LLMManager()
