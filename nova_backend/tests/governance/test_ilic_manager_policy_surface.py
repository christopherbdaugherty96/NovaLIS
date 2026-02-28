from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LLM_MANAGER = PROJECT_ROOT / "src" / "llm" / "llm_manager.py"
LLM_MANAGER_VLOCK = PROJECT_ROOT / "src" / "llm" / "llm_manager_vlock.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_llm_managers_disable_redirects_and_use_ilic_validation():
    for path in (LLM_MANAGER, LLM_MANAGER_VLOCK):
        text = _text(path)
        assert "validate_and_lock_base_url" in text
        assert "allow_redirects=False" in text
        assert "build_hardened_session" in text


def test_llm_managers_do_not_use_proxy_env_variables_directly():
    forbidden = ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY", "os.getenv("]
    for path in (LLM_MANAGER, LLM_MANAGER_VLOCK):
        text = _text(path)
        hits = [tok for tok in forbidden if tok in text]
        assert not hits, f"Proxy/env logic found in {path}: {hits}"


def test_llm_managers_emit_ilic_events_not_action_events():
    for path in (LLM_MANAGER, LLM_MANAGER_VLOCK):
        text = _text(path)
        assert "ILIC_" in text
        assert "ACTION_ATTEMPTED" not in text
        assert "ACTION_COMPLETED" not in text
