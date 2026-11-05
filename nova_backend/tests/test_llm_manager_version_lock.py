from pathlib import Path

import src.llm.llm_manager as mod
from src.llm.model_network_mediator import ModelNetworkMediatorError, ModelResponse


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
                    data={"models": [{"name": "gemma4:e4b", "digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}]},
                ),
            ]
        )
    )

    assert manager._get_model_digest() == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def test_check_model_version_accepts_trusted_hash_from_tags_fallback(tmp_path, monkeypatch):
    wrapper_path = tmp_path / "inference_wrapper.py"
    wrapper_path.write_text("def run():\n    return 'ok'\n", encoding="utf-8")

    model_hash_path = tmp_path / "current_model_hash.txt"
    trusted_digest = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
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


def test_generate_retries_with_fallback_after_primary_network_failure():
    captured_models = []

    class _PrimaryFailsNetwork:
        def request_json(self, **kwargs):
            captured_models.append(kwargs["json_payload"]["model"])
            if len(captured_models) == 1:
                raise ModelNetworkMediatorError("model requires more system memory")
            return ModelResponse(
                status_code=200,
                data={"message": {"content": "A GPU is a processor for parallel work."}},
            )

    manager = _build_manager(_PrimaryFailsNetwork())
    manager.fallback_model = "gemma2:2b"

    result = manager.generate("what is a GPU?", request_id="fallback-proof")

    assert result == "A GPU is a processor for parallel work."
    assert captured_models == ["gemma4:e4b", "gemma2:2b"]
    assert manager.active_model == "gemma2:2b"
    assert manager.failure_count == 0
    assert manager.circuit_open_until == 0


def test_fallback_retry_uses_smaller_context_window():
    captured_options = []

    class _PrimaryFailsNetwork:
        def request_json(self, **kwargs):
            captured_options.append(dict(kwargs["json_payload"]["options"]))
            if len(captured_options) == 1:
                raise ModelNetworkMediatorError("model requires more system memory")
            return ModelResponse(
                status_code=200,
                data={"message": {"content": "fallback ok"}},
            )

    manager = _build_manager(_PrimaryFailsNetwork())
    manager.fallback_model = "gemma2:2b"
    manager.default_options["num_ctx"] = 32768
    manager.default_options["num_predict"] = 512

    assert manager.generate("explain local AI") == "fallback ok"
    assert captured_options[0]["num_ctx"] == 32768
    assert captured_options[1]["num_ctx"] == 4096
    assert captured_options[1]["num_predict"] == min(384, mod.OLLAMA_NUM_PREDICT)


def test_try_recover_primary_requires_chat_probe_success():
    class _PrimaryStillFailsNetwork:
        def request_json(self, **kwargs):
            assert kwargs["json_payload"]["model"] == "gemma4:e4b"
            raise ModelNetworkMediatorError("model requires more system memory")

    manager = _build_manager(_PrimaryStillFailsNetwork())
    manager.fallback_model = "gemma2:2b"
    manager._using_fallback = True

    assert manager.try_recover_primary() is False
    assert manager.active_model == "gemma2:2b"


def test_try_recover_primary_switches_back_after_chat_probe_success():
    captured = {}

    class _PrimaryRecoveredNetwork:
        def request_json(self, **kwargs):
            captured.update(kwargs)
            return ModelResponse(status_code=200, data={"message": {"content": "ok"}})

    manager = _build_manager(_PrimaryRecoveredNetwork())
    manager.fallback_model = "gemma2:2b"
    manager._using_fallback = True

    assert manager.try_recover_primary() is True
    assert manager.active_model == "gemma4:e4b"
    assert captured["json_payload"]["options"]["num_predict"] == 1
    assert captured["json_payload"]["options"]["num_ctx"] == 512


def test_unavailable_model_digest_cannot_be_confirmed(tmp_path, monkeypatch):
    """Owner confirmation must never lock the synthetic fetch_failed identity."""
    from src.governor.exceptions import LedgerWriteFailed

    class _UnavailableNetwork:
        def request_json(self, **_kwargs):
            raise ModelNetworkMediatorError("Data-Out denied (evidence_unavailable).")

    manager = _build_manager(_UnavailableNetwork())
    manager.inference_blocked = True
    hash_path = tmp_path / "model_hash.txt"
    wrapper_path = tmp_path / "inference_wrapper.py"
    wrapper_path.write_text("# fixture\n", encoding="utf-8")
    monkeypatch.setattr(mod, "MODEL_HASH_FILE", hash_path)
    monkeypatch.setattr(mod, "WRAPPER_PATH", wrapper_path)
    monkeypatch.setattr(
        manager, "_log_model_updated",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("unverified identity must not generate an update receipt")
        ),
    )

    try:
        manager.confirm_model_update()
    except (ValueError, ModelNetworkMediatorError, LedgerWriteFailed):
        pass

    assert manager.inference_blocked is True
    assert not hash_path.exists()


def test_malformed_or_placeholder_model_digest_is_rejected():
    for invalid in ("fetch_failed", "unknown", "sha256:trusted", "", "a" * 63):
        manager = _build_manager(
            _FakeNetwork(
                [
                    ModelResponse(status_code=200, data={"digest": invalid}),
                    ModelResponse(
                        status_code=200,
                        data={"models": [{"name": "gemma4:e4b", "digest": invalid}]},
                    ),
                ]
            )
        )
        assert manager._get_model_digest() is None


def test_model_digest_must_match_exact_selected_model_from_tags():
    valid = "b" * 64
    manager = _build_manager(
        _FakeNetwork(
            [
                ModelResponse(status_code=200, data={"model_info": {}}),
                ModelResponse(
                    status_code=200,
                    data={"models": [
                        {"name": "gemma2:2b", "digest": valid},
                    ]},
                ),
            ]
        )
    )
    assert manager._get_model_digest() is None
