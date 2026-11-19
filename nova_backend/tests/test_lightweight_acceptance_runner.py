from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

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
    assert (
        MODULE._score(0, "RAM is temporary while storage is persistent.")
        == "PROVISIONAL_KEYWORD_MATCH"
    )
    assert MODULE._score(1, "Cedar is pending for Tuesday.") == "PROVISIONAL_KEYWORD_MATCH"
    assert MODULE._score(5, "Cedar remains pending for Tuesday.") == "PROVISIONAL_KEYWORD_MATCH"
    assert MODULE._score(5, "Cedar is pending.") == "PROVISIONAL_KEYWORD_PARTIAL"
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


def test_model_hash_path_uses_runtime_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime_root = tmp_path / "authoritative-runtime"
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(runtime_root))
    path = MODULE.authoritative_model_hash_path(Path(__file__).resolve().parents[2])
    assert path == runtime_root / "models/current_model_hash.txt"


class _BlockingWebSocket:
    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []
        self.closed: tuple[int, str] | None = None

    async def send(self, payload: str) -> None:
        self.sent.append(json.loads(payload))

    async def recv(self) -> str:
        await asyncio.Event().wait()
        raise AssertionError("unreachable")

    async def close(self, *, code: int, reason: str) -> None:
        self.closed = (code, reason)


@pytest.mark.asyncio
async def test_memory_watchdog_interrupts_active_turn(monkeypatch: pytest.MonkeyPatch) -> None:
    unsafe = MODULE.MemorySample(
        available_bytes=256 * 1024**2,
        physical_used_percent=96.0,
        committed_bytes=None,
        commit_limit_bytes=None,
    )
    monkeypatch.setattr(MODULE, "memory_sample", lambda: unsafe)
    websocket = _BlockingWebSocket()

    cancellation_calls: list[str] = []

    def cancel() -> MODULE.CleanupResult:
        cancellation_calls.append("cancelled")
        return MODULE.CleanupResult("cancel_active_inference_backend")

    result = await MODULE._run_turn(
        websocket,
        "prompt",
        0,
        5.0,
        512 * 1024**2,
        cancel,
    )

    assert result.error == "RuntimeSafetyStop: available_physical_memory_below_runtime_stop"
    assert websocket.closed == (1011, "available_physical_memory_below_runtime_stop")
    assert cancellation_calls == ["cancelled"]
    assert result.total_seconds is not None and result.total_seconds < 1.0


@pytest.mark.asyncio
async def test_turn_timeout_is_one_overall_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    safe = MODULE.MemorySample(
        available_bytes=4 * 1024**3,
        physical_used_percent=50.0,
        committed_bytes=None,
        commit_limit_bytes=None,
    )
    monkeypatch.setattr(MODULE, "memory_sample", lambda: safe)
    websocket = _BlockingWebSocket()
    cancellation_calls: list[str] = []

    def cancel() -> MODULE.CleanupResult:
        cancellation_calls.append("cancelled")
        return MODULE.CleanupResult("cancel_active_inference_backend")

    result = await MODULE._run_turn(
        websocket,
        "prompt",
        0,
        0.05,
        512 * 1024**2,
        cancel,
    )

    assert result.error == "TurnDeadlineExceeded: overall turn deadline of 0.05s exceeded"
    assert websocket.closed == (1011, "acceptance turn deadline exceeded")
    assert cancellation_calls == ["cancelled"]


def test_cleanup_process_records_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_timeout(*args: object, **kwargs: object) -> None:
        raise TimeoutError("cleanup stuck")

    monkeypatch.setattr(MODULE.subprocess, "run", raise_timeout)
    result = MODULE._cleanup_process("stop_nova_backend", ["python"], timeout=1)
    assert result.error == "TimeoutError: cleanup stuck"


def test_cleanup_process_records_nonzero_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    completed = MODULE.subprocess.CompletedProcess(["python"], 3)
    monkeypatch.setattr(MODULE.subprocess, "run", lambda *args, **kwargs: completed)
    result = MODULE._cleanup_process("stop_nova_backend", ["python"], timeout=1)
    assert result.error == "exit_code_3"


def test_missing_unload_executable_is_not_usable() -> None:
    executable, reason = MODULE._validated_unload_executable(None)
    assert executable is None
    assert reason == "model_unload_executable_missing"


def test_invalid_unload_executable_is_not_usable(tmp_path: Path) -> None:
    executable, reason = MODULE._validated_unload_executable(tmp_path / "missing-ollama.exe")
    assert executable is None
    assert reason == "model_unload_executable_invalid"


def test_nonworking_unload_executable_is_not_usable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "ollama.exe"
    path.touch()
    completed = MODULE.subprocess.CompletedProcess([str(path), "--version"], 1)
    monkeypatch.setattr(MODULE.subprocess, "run", lambda *args, **kwargs: completed)
    executable, reason = MODULE._validated_unload_executable(path)
    assert executable is None
    assert reason == "model_unload_executable_unusable"


def test_failed_model_unload_is_recorded(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    failure = MODULE.CleanupResult("stop_test_model", "exit_code_1")
    monkeypatch.setattr(MODULE, "_cleanup_process", lambda *args, **kwargs: failure)
    assert MODULE._unload_owned_model(tmp_path / "ollama.exe") == failure


def test_cleanup_failure_downgrades_provisional_result_to_hold() -> None:
    evidence = {"verdict": "PROVISIONAL"}
    cleanup = [MODULE.CleanupResult("stop_nova_backend", "exit_code_1")]
    MODULE._record_cleanup_results(evidence, cleanup)
    assert evidence["verdict_before_cleanup_failure"] == "PROVISIONAL"
    assert evidence["verdict"] == "HOLD"


class _FakeProcess:
    def __init__(self, pid: int, created: float, command: list[str]) -> None:
        self.pid = pid
        self._created = created
        self._command = command
        self.terminated = False

    def create_time(self) -> float:
        return self._created

    def cmdline(self) -> list[str]:
        return self._command

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        raise AssertionError("graceful termination should have completed")


def test_owned_cleanup_terminates_only_matching_backend_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backend = tmp_path / "nova_backend"
    process = _FakeProcess(
        123,
        10.0,
        [str(backend / "venv/python.exe"), "-m", "uvicorn", "src.brain_server:app"],
    )
    monkeypatch.setattr(MODULE.psutil, "Process", lambda pid: process)
    monkeypatch.setattr(MODULE.psutil, "wait_procs", lambda processes, timeout: (processes, []))

    result = MODULE._terminate_owned_backends(
        {123: MODULE.OwnedProcess(123, 10.0)},
        tmp_path,
        action="stop_owned_nova_backend",
    )

    assert result.error is None
    assert process.terminated is True


def test_owned_cleanup_refuses_reused_pid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backend = tmp_path / "nova_backend"
    process = _FakeProcess(
        123,
        20.0,
        [str(backend / "venv/python.exe"), "-m", "uvicorn", "src.brain_server:app"],
    )
    monkeypatch.setattr(MODULE.psutil, "Process", lambda pid: process)
    monkeypatch.setattr(MODULE.psutil, "wait_procs", lambda processes, timeout: (processes, []))

    result = MODULE._terminate_owned_backends(
        {123: MODULE.OwnedProcess(123, 10.0)},
        tmp_path,
        action="stop_owned_nova_backend",
    )

    assert result.error == "pid_123_identity_changed"
    assert process.terminated is False


def test_startup_timeout_still_attempts_owned_backend_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    python = root / "nova_backend/venv/Scripts/python.exe"
    python.parent.mkdir(parents=True)
    python.touch()
    (root / "scripts").mkdir()
    args = SimpleNamespace(
        repo_root=root,
        expected_commit="a" * 40,
        expected_digest="b" * 64,
        confirm_model_update=False,
        minimum_start_gb=2.0,
        runtime_stop_gb=0.5,
        turn_timeout=120.0,
        output=root / "evidence.json",
        ollama_executable=None,
    )
    safe = MODULE.MemorySample(
        available_bytes=4 * 1024**3,
        physical_used_percent=50.0,
        committed_bytes=4 * 1024**3,
        commit_limit_bytes=16 * 1024**3,
    )
    def start(*args: object, **kwargs: object) -> None:
        owned = kwargs["owned"]
        assert isinstance(owned, dict)
        owned[123] = MODULE.OwnedProcess(123, 1.0)
        raise MODULE.subprocess.TimeoutExpired("start", 60)

    terminated: list[tuple[int, ...]] = []

    def terminate(
        owned: dict[int, MODULE.OwnedProcess], unused_root: Path, *, action: str
    ) -> MODULE.CleanupResult:
        terminated.append(tuple(owned))
        return MODULE.CleanupResult(action)

    captured: dict[str, object] = {}
    monkeypatch.setattr(MODULE, "parse_args", lambda: args)
    monkeypatch.setattr(MODULE, "_git_head", lambda unused: args.expected_commit)
    monkeypatch.setattr(MODULE, "_port_open", lambda: False)
    monkeypatch.setattr(MODULE, "memory_sample", lambda: safe)
    monkeypatch.setattr(MODULE, "_model_is_resident", lambda: True)
    monkeypatch.setattr(MODULE, "_start_backend_with_ownership", start)
    monkeypatch.setattr(MODULE, "_terminate_owned_backends", terminate)
    monkeypatch.setattr(
        MODULE,
        "_unload_owned_model",
        lambda executable: (_ for _ in ()).throw(AssertionError("pre-existing model unloaded")),
    )
    monkeypatch.setattr(MODULE, "_write_evidence", lambda path, payload: captured.update(payload))

    assert MODULE.main() == 2
    assert terminated == [(123,)]
    assert captured["verdict"] == "HOLD"
    assert captured["cleanup"] == [
        {"action": "stop_owned_nova_backend", "error": None},
    ]


def test_nonresident_model_without_unload_path_holds_before_backend_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    python = root / "nova_backend/venv/Scripts/python.exe"
    python.parent.mkdir(parents=True)
    python.touch()
    args = SimpleNamespace(
        repo_root=root,
        expected_commit="a" * 40,
        expected_digest="b" * 64,
        confirm_model_update=False,
        minimum_start_gb=2.0,
        runtime_stop_gb=0.5,
        turn_timeout=120.0,
        output=root / "evidence.json",
        ollama_executable=None,
    )
    safe = MODULE.MemorySample(
        available_bytes=4 * 1024**3,
        physical_used_percent=50.0,
        committed_bytes=4 * 1024**3,
        commit_limit_bytes=16 * 1024**3,
    )
    captured: dict[str, object] = {}
    monkeypatch.setattr(MODULE, "parse_args", lambda: args)
    monkeypatch.setattr(MODULE, "_git_head", lambda unused: args.expected_commit)
    monkeypatch.setattr(MODULE, "_port_open", lambda: False)
    monkeypatch.setattr(MODULE, "memory_sample", lambda: safe)
    monkeypatch.setattr(MODULE, "_model_is_resident", lambda: False)
    monkeypatch.setattr(
        MODULE,
        "_start_backend_with_ownership",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("backend started")),
    )
    monkeypatch.setattr(MODULE, "_write_evidence", lambda path, payload: captured.update(payload))

    assert MODULE.main() == 2
    assert captured["preflight"] == "model_unload_executable_missing"
    assert captured["model_residency_before"] == "not_resident"
    assert captured["verdict"] == "HOLD"


def test_unknown_model_residency_holds_before_backend_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    python = root / "nova_backend/venv/Scripts/python.exe"
    python.parent.mkdir(parents=True)
    python.touch()
    args = SimpleNamespace(
        repo_root=root,
        expected_commit="a" * 40,
        expected_digest="b" * 64,
        confirm_model_update=False,
        minimum_start_gb=2.0,
        runtime_stop_gb=0.5,
        turn_timeout=120.0,
        output=root / "evidence.json",
        ollama_executable=tmp_path / "ollama.exe",
    )
    safe = MODULE.MemorySample(
        available_bytes=4 * 1024**3,
        physical_used_percent=50.0,
        committed_bytes=4 * 1024**3,
        commit_limit_bytes=16 * 1024**3,
    )
    captured: dict[str, object] = {}
    monkeypatch.setattr(MODULE, "parse_args", lambda: args)
    monkeypatch.setattr(MODULE, "_git_head", lambda unused: args.expected_commit)
    monkeypatch.setattr(MODULE, "_port_open", lambda: False)
    monkeypatch.setattr(MODULE, "memory_sample", lambda: safe)
    monkeypatch.setattr(
        MODULE,
        "_model_is_resident",
        lambda: (_ for _ in ()).throw(ConnectionError("Ollama unavailable")),
    )
    monkeypatch.setattr(
        MODULE,
        "_start_backend_with_ownership",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("backend started")),
    )
    monkeypatch.setattr(MODULE, "_write_evidence", lambda path, payload: captured.update(payload))

    assert MODULE.main() == 2
    assert captured["preflight"] == "model_residency_unknown"
    assert captured["model_residency_before"] == "unknown"
    assert captured["verdict"] == "HOLD"

