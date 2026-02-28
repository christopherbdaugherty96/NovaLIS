# src/llm/llm_manager_vlock.py

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

import requests

from src.ledger.writer import LedgerWriter
from src.governor.exceptions import LedgerWriteFailed
from .ilic import (
    LockedILICConfig,
    ILICValidationError,
    validate_and_lock_base_url,
    build_hardened_session,
    metadata_timeout,
    inference_timeout,
)
from .system_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

MODEL_HASH_FILE = Path(__file__).resolve().parents[1] / "models" / "current_model_hash.txt"
WRAPPER_PATH = Path(__file__).parent / "inference_wrapper.py"


def compute_model_hash(
    model_digest: str,
    system_prompt: str,
    wrapper_code: str,
    params: Dict[str, Any]
) -> str:
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
    """Ollama LLM integration with constitutional version locking and ILIC hardening."""

    def __init__(
        self,
        model: str = "phi3:mini",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.timeout = 30
        self.system_prompt = SYSTEM_PROMPT
        self._ledger = LedgerWriter()

        try:
            self._ilic: LockedILICConfig = validate_and_lock_base_url(base_url)
        except ILICValidationError as err:
            self._ilic = LockedILICConfig(base_url="http://localhost:11434", host="localhost", port=11434)
            self.session = build_hardened_session()
            self.failure_count = 0
            self.circuit_open_until = 0
            self.default_options = {
                "temperature": 0.4,
                "num_predict": 256,
                "num_ctx": 4096,
                "top_k": 40,
                "repeat_penalty": 1.1,
                "stop": ["\n\n", "User:", "Human:"],
            }
            self.inference_blocked = True
            self._log_ilic_event("ILIC_VALIDATION_FAILED", {"error": str(err), "base_url": base_url})
            return

        self.session = build_hardened_session()

        self.failure_count = 0
        self.circuit_open_until = 0

        self.default_options = {
            "temperature": 0.4,
            "num_predict": 256,
            "num_ctx": 4096,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "stop": ["\n\n", "User:", "Human:"],
        }

        self.inference_blocked = False
        self._check_model_version()

    @property
    def base_url(self) -> str:
        return self._ilic.base_url

    def _log_ilic_event(self, event_type: str, metadata: Dict[str, Any]) -> None:
        try:
            self._ledger.log_event(event_type, metadata)
        except LedgerWriteFailed:
            pass

    def _get_model_digest(self) -> Optional[str]:
        try:
            resp = self.session.post(
                f"{self.base_url}/api/show",
                json={"model": self.model},
                timeout=metadata_timeout(),
                allow_redirects=False,
            )
            self._log_ilic_event("ILIC_REQUEST", {"endpoint": "/api/show", "status_code": resp.status_code})
            resp.raise_for_status()
            data = resp.json()
            return data.get("digest")
        except Exception as e:
            self._log_ilic_event("ILIC_FAILURE", {"endpoint": "/api/show", "error": str(e)})
            logger.warning(f"Could not fetch model digest: {e}")
            return None

    def _compute_current_hash(self) -> str:
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
        self.inference_blocked = True
        logger.warning("Model inference blocked due to version mismatch.")

    def _log_model_updated(
        self,
        previous_hash: Optional[str],
        new_hash: str,
        user_confirmed: bool,
    ) -> None:
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
            self._block_inference()
            raise

    def _check_model_version(self):
        MODEL_HASH_FILE.parent.mkdir(parents=True, exist_ok=True)

        computed = self._compute_current_hash()

        if MODEL_HASH_FILE.exists():
            stored = MODEL_HASH_FILE.read_text().strip()
            if stored == computed:
                logger.info("Model version OK.")
                return
            logger.warning("Model version mismatch. Blocking inference.")
            self._block_inference()
            self._log_model_updated(stored, computed, user_confirmed=False)
        else:
            logger.info("First model run – blocking inference until confirmed.")
            self._block_inference()
            self._log_model_updated(None, computed, user_confirmed=False)

    def confirm_model_update(self):
        if not self.inference_blocked:
            return

        computed = self._compute_current_hash()
        previous = None
        if MODEL_HASH_FILE.exists():
            previous = MODEL_HASH_FILE.read_text().strip()
        MODEL_HASH_FILE.write_text(computed)
        self.inference_blocked = False
        self._log_model_updated(previous, computed, user_confirmed=True)
        logger.info("Model update confirmed. Inference unblocked.")

    def _record_failure(self):
        self.failure_count += 1
        if self.failure_count >= 3:
            self.circuit_open_until = time.time() + 30
            logger.warning("Circuit breaker opened. Will retry after 30 seconds.")
            self.failure_count = 0

    def generate(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        if self.inference_blocked:
            logger.error("Generate called while model is blocked.")
            return None

        now = time.time()
        if now < self.circuit_open_until:
            logger.warning("Circuit breaker open. Skipping request.")
            return None

        system = system_prompt or self.system_prompt

        try:
            from .inference_wrapper import run_inference

            result = run_inference(
                base_url=self.base_url,
                model=self.model,
                prompt=prompt,
                system=system,
                options=self.default_options,
                timeout=inference_timeout(),
                allow_redirects=False,
                trust_env=False,
            )
            self._log_ilic_event("ILIC_REQUEST", {"endpoint": "/api/generate", "status": "ok"})
            self.failure_count = 0
            return result

        except requests.exceptions.Timeout:
            self._log_ilic_event("ILIC_FAILURE", {"endpoint": "/api/generate", "error": "timeout"})
            logger.warning(f"LLM request timed out after {self.timeout}s")
            self._record_failure()
        except requests.exceptions.ConnectionError:
            self._log_ilic_event("ILIC_FAILURE", {"endpoint": "/api/generate", "error": "connection_error"})
            logger.error("Cannot connect to Ollama. Is it running?")
            self._record_failure()
        except Exception as e:
            self._log_ilic_event("ILIC_FAILURE", {"endpoint": "/api/generate", "error": str(e)})
            logger.error(f"LLM error: {e}")
            self._record_failure()

        return None

    def health_check(self) -> bool:
        try:
            resp = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=metadata_timeout(),
                allow_redirects=False,
            )
            self._log_ilic_event("ILIC_REQUEST", {"endpoint": "/api/tags", "status_code": resp.status_code})
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                return any(self.model in m.get("name", "") for m in models)
        except Exception as e:
            self._log_ilic_event("ILIC_FAILURE", {"endpoint": "/api/tags", "error": str(e)})
        return False


llm_manager = LLMManager()
