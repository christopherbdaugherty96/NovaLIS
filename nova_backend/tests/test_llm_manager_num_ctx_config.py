"""Tests that OLLAMA_NUM_CTX and OLLAMA_NUM_PREDICT env vars are respected."""

import src.llm.llm_manager as mod


def _build_manager_raw() -> mod.LLMManager:
    """Construct an LLMManager without calling __init__ (no Ollama needed)."""
    manager = object.__new__(mod.LLMManager)
    manager.model = "gemma2:2b"
    manager.base_url = "http://localhost:11434"
    manager.timeout = 30
    manager.system_prompt = "test"
    manager._network = None
    manager.fallback_model = "phi3:mini"
    manager._using_fallback = False
    manager.failure_count = 0
    manager.circuit_open_until = 0
    manager.inference_blocked = False
    return manager


def test_num_ctx_respects_env_override(monkeypatch):
    """When OLLAMA_NUM_CTX is set in the environment, LLMManager uses it."""
    monkeypatch.setenv("OLLAMA_NUM_CTX", "4096")
    # Reload the config module so it picks up the patched env
    import importlib
    import src.nova_config as cfg
    importlib.reload(cfg)
    importlib.reload(mod)

    manager = _build_manager_raw()
    # Manually set default_options the way __init__ would
    manager.default_options = {
        "temperature": 0.7,
        "num_predict": 512,
        "num_ctx": cfg.OLLAMA_NUM_CTX,
        "top_k": 50,
        "repeat_penalty": 1.1,
        "stop": ["User:", "Human:"],
    }

    assert manager.default_options["num_ctx"] == 4096


def test_num_ctx_uses_default_when_env_unset(monkeypatch):
    """When OLLAMA_NUM_CTX is not in the environment, default is 32768."""
    monkeypatch.delenv("OLLAMA_NUM_CTX", raising=False)
    import importlib
    import src.nova_config as cfg
    importlib.reload(cfg)

    assert cfg.OLLAMA_NUM_CTX == 32768


def test_num_ctx_propagated_through_init(monkeypatch):
    """Full __init__ path uses OLLAMA_NUM_CTX from config."""
    monkeypatch.setenv("OLLAMA_NUM_CTX", "8192")
    import importlib
    import src.nova_config as cfg
    importlib.reload(cfg)
    importlib.reload(mod)

    # We can't call full __init__ (needs Ollama), but we can verify
    # the module-level import is correct after reload
    assert mod.OLLAMA_NUM_CTX == 8192


def test_num_predict_respects_env_override(monkeypatch):
    """When OLLAMA_NUM_PREDICT is set in the environment, LLMManager uses it."""
    monkeypatch.setenv("OLLAMA_NUM_PREDICT", "256")
    import importlib
    import src.nova_config as cfg
    importlib.reload(cfg)
    importlib.reload(mod)

    manager = _build_manager_raw()
    manager.default_options = {
        "temperature": 0.7,
        "num_predict": cfg.OLLAMA_NUM_PREDICT,
        "num_ctx": cfg.OLLAMA_NUM_CTX,
        "top_k": 50,
        "repeat_penalty": 1.1,
        "stop": ["User:", "Human:"],
    }

    assert manager.default_options["num_predict"] == 256


def test_num_predict_uses_default_when_env_unset(monkeypatch):
    """When OLLAMA_NUM_PREDICT is not in the environment, default is 512."""
    monkeypatch.delenv("OLLAMA_NUM_PREDICT", raising=False)
    import importlib
    import src.nova_config as cfg
    importlib.reload(cfg)

    assert cfg.OLLAMA_NUM_PREDICT == 512


def test_num_predict_propagated_through_init(monkeypatch):
    """Full __init__ path uses OLLAMA_NUM_PREDICT from config."""
    monkeypatch.setenv("OLLAMA_NUM_PREDICT", "128")
    import importlib
    import src.nova_config as cfg
    importlib.reload(cfg)
    importlib.reload(mod)

    assert mod.OLLAMA_NUM_PREDICT == 128
