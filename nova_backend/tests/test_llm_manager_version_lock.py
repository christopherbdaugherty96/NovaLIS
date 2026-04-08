from pathlib import Path

import src.llm.llm_manager as mod
from src.llm.model_network_mediator import ModelResponse


class _FakeNetwork:
    def __init__(self, responses):
        self._responses = list(responses)

    def request_json(self, **_kwargs):
        if not self._responses:
            raise AssertionError("Unexpected network call.")
        return self._responses.pop(0)


def _build_manager(network: _FakeNetwork) -> mod.LLMManager:
    manager = object.__new__(mod.LLMManager)
    manager.model = "gemma4:e4b"
    manager.base_url = "http://localhost:11434"
    manager.timeout = 30
    manager.system_prompt = "test system prompt"
    manager._network = network
    manager.fallback_model = ""
    manager._using_fallback = False
    manager.failure_count = 0
    manager.circuit_open_until = 0
    manager.default_options = {
        "temperature": 0.4,
        "num_predict": 256,
        "num_ctx": 4096,
        "top_k": 40,
        "repeat_penalty": 1.1,
        "stop": ["\n\n", "User:", "Human:"],
    }
    manager.inference_blocked = False
    return manager


def test_get_model_digest_falls_back_to_tags_when_show_omits_digest():
    manager = _build_manager(
        _FakeNetwork(
            [
                ModelResponse(status_code=200, data={"model_info": {"general.architecture": "gemma4"}}),
                ModelResponse(
                    status_code=200,
                    data={"models": [{"name": "gemma4:e4b", "digest": "sha256:trusted"}]},
                ),
            ]
        )
    )

    assert manager._get_model_digest() == "sha256:trusted"


def test_check_model_version_accepts_trusted_hash_from_tags_fallback(tmp_path, monkeypatch):
    wrapper_path = tmp_path / "inference_wrapper.py"
    wrapper_path.write_text("def run():\n    return 'ok'\n", encoding="utf-8")

    model_hash_path = tmp_path / "current_model_hash.txt"
    trusted_digest = "sha256:trusted"
    trusted_hash = mod.compute_model_hash(
        trusted_digest,
        "test system prompt",
        wrapper_path.read_text(encoding="utf-8"),
        {
            "temperature": 0.4,
            "num_predict": 256,
            "num_ctx": 4096,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "stop": ["\n\n", "User:", "Human:"],
        },
    )
    model_hash_path.write_text(trusted_hash, encoding="utf-8")

    monkeypatch.setattr(mod, "WRAPPER_PATH", Path(wrapper_path))
    monkeypatch.setattr(mod, "MODEL_HASH_FILE", Path(model_hash_path))

    manager = _build_manager(
        _FakeNetwork(
            [
                ModelResponse(status_code=200, data={"license": "MIT", "model_info": {}}),
                ModelResponse(
                    status_code=200,
                    data={"models": [{"name": "gemma4:e4b", "digest": trusted_digest}]},
                ),
            ]
        )
    )

    manager._check_model_version()

    assert manager.inference_blocked is False


def test_generate_uses_explicit_timeout_override():
    captured = {}

    class _CaptureNetwork:
        def request_json(self, **kwargs):
            captured.update(kwargs)
            return ModelResponse(
                status_code=200,
                data={"message": {"content": "Structured analysis is available."}},
            )

    manager = _build_manager(_CaptureNetwork())
    manager.timeout = 30

    result = manager.generate(
        "Why does governed access matter?",
        system_prompt="You are concise.",
        timeout=90,
        request_id="timeout-proof",
    )

    assert result == "Structured analysis is available."
    assert captured.get("timeout") == 90.0
