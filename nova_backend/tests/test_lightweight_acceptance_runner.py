from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "run_lightweight_acceptance.py"
SPEC = importlib.util.spec_from_file_location("lightweight_acceptance", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_fixed_lightweight_profile_and_prompts() -> None:
    assert MODULE.MODEL == "gemma2:2b"
    assert MODULE.NUM_CTX == 2048
    assert MODULE.NUM_PREDICT == 128
    assert len(MODULE.CONTEXT_PROMPTS) == 5
    assert "Cedar" in MODULE.CONTEXT_PROMPTS[0]
    assert "Tuesday" in MODULE.CONTEXT_PROMPTS[0]
    assert "pending" in MODULE.CONTEXT_PROMPTS[0]


def test_resource_gate_rejects_low_physical_memory() -> None:
    sample = MODULE.MemorySample(
        available_bytes=256 * 1024**2,
        physical_used_percent=96.0,
        committed_bytes=4 * 1024**3,
        commit_limit_bytes=16 * 1024**3,
    )
    passed, reason = MODULE.resource_gate(sample, minimum_available_bytes=2 * 1024**3)
    assert passed is False
    assert reason == "available_physical_memory_below_gate"


def test_resource_gate_rejects_low_commit_headroom() -> None:
    sample = MODULE.MemorySample(
        available_bytes=3 * 1024**3,
        physical_used_percent=60.0,
        committed_bytes=14 * 1024**3,
        commit_limit_bytes=16 * 1024**3,
    )
    passed, reason = MODULE.resource_gate(sample, minimum_available_bytes=2 * 1024**3)
    assert passed is False
    assert reason == "commit_headroom_below_gate"


def test_runtime_stop_rejects_severe_pressure() -> None:
    sample = MODULE.MemorySample(
        available_bytes=300 * 1024**2,
        physical_used_percent=96.0,
        committed_bytes=None,
        commit_limit_bytes=None,
    )
    passed, reason = MODULE.runtime_safe(sample, minimum_available_bytes=512 * 1024**2)
    assert passed is False
    assert reason == "available_physical_memory_below_runtime_stop"


def test_scoring_keeps_performance_separate_from_content() -> None:
    assert MODULE._score(0, "RAM is temporary while storage is persistent.") == "PASS"
    assert MODULE._score(1, "Cedar is pending for Tuesday.") == "PASS"
    assert MODULE._score(5, "Cedar remains pending for Tuesday.") == "PASS"
    assert MODULE._score(5, "Cedar is pending.") == "PARTIAL"
    assert MODULE._score(5, "") == "FAIL"


def test_fingerprint_is_stable_for_same_inputs(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "nova_backend/src/llm"
    prompt_dir.mkdir(parents=True)
    (prompt_dir / "system_prompt.py").write_text("SYSTEM_PROMPT = 'system'\n", encoding="utf-8")
    (prompt_dir / "inference_wrapper.py").write_text("wrapper\n", encoding="utf-8")
    digest = "a" * 64
    first, params = MODULE.expected_fingerprint(tmp_path, digest)
    second, _ = MODULE.expected_fingerprint(tmp_path, digest)
    assert first == second
    assert params["num_ctx"] == 2048
    assert params["num_predict"] == 128

