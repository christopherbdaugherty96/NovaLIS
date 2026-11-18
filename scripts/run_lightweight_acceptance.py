#!/usr/bin/env python3
"""Run Nova's bounded low-overhead local-model acceptance.

This is a test-only owner acceptance tool. It does not select production defaults,
download models, enable providers, or grant Nova execution authority.
"""

from __future__ import annotations

import argparse
import ast
import asyncio
import ctypes
import hashlib
import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil
import websockets

MODEL = "gemma2:2b"
NUM_CTX = 2048
NUM_PREDICT = 128
MINIMAL_PROMPT = "Explain the difference between RAM and computer storage in one sentence."
CONTEXT_PROMPTS = (
    "For this test, my imaginary project is called Cedar, its target day is Tuesday, "
    "and its status is pending. Repeat those three details briefly.",
    "What is the project's name?",
    "Which day did I specify?",
    "What is its current status?",
    "Summarize all three project details in one sentence.",
)


@dataclass(frozen=True)
class MemorySample:
    available_bytes: int
    physical_used_percent: float
    committed_bytes: int | None
    commit_limit_bytes: int | None


@dataclass
class TurnResult:
    prompt: str
    response: str = ""
    error: str | None = None
    first_chat_seconds: float | None = None
    total_seconds: float | None = None
    minimum_available_bytes: int | None = None
    maximum_physical_used_percent: float | None = None
    score: str = "FAIL"


def _windows_commit() -> tuple[int | None, int | None]:
    if os.name != "nt":
        return None, None

    class PerformanceInformation(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("CommitTotal", ctypes.c_size_t),
            ("CommitLimit", ctypes.c_size_t),
            ("CommitPeak", ctypes.c_size_t),
            ("PhysicalTotal", ctypes.c_size_t),
            ("PhysicalAvailable", ctypes.c_size_t),
            ("SystemCache", ctypes.c_size_t),
            ("KernelTotal", ctypes.c_size_t),
            ("KernelPaged", ctypes.c_size_t),
            ("KernelNonpaged", ctypes.c_size_t),
            ("PageSize", ctypes.c_size_t),
            ("HandleCount", ctypes.c_ulong),
            ("ProcessCount", ctypes.c_ulong),
            ("ThreadCount", ctypes.c_ulong),
        ]

    info = PerformanceInformation()
    info.cb = ctypes.sizeof(info)
    if not ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(info), info.cb):
        return None, None
    return info.CommitTotal * info.PageSize, info.CommitLimit * info.PageSize


def memory_sample() -> MemorySample:
    memory = psutil.virtual_memory()
    committed, commit_limit = _windows_commit()
    return MemorySample(
        available_bytes=int(memory.available),
        physical_used_percent=float(memory.percent),
        committed_bytes=committed,
        commit_limit_bytes=commit_limit,
    )


def resource_gate(sample: MemorySample, *, minimum_available_bytes: int) -> tuple[bool, str]:
    if sample.available_bytes < minimum_available_bytes:
        return False, "available_physical_memory_below_gate"
    if sample.commit_limit_bytes and sample.committed_bytes:
        if sample.commit_limit_bytes - sample.committed_bytes < 3 * 1024**3:
            return False, "commit_headroom_below_gate"
    return True, "pass"


def runtime_safe(sample: MemorySample, *, minimum_available_bytes: int) -> tuple[bool, str]:
    if sample.available_bytes < minimum_available_bytes:
        return False, "available_physical_memory_below_runtime_stop"
    if sample.physical_used_percent > 95.0:
        return False, "physical_memory_above_runtime_stop"
    return True, "pass"


def _literal_assignment(path: Path, name: str) -> str:
    module = ast.parse(path.read_text(encoding="utf-8"))
    for node in module.body:
        value: ast.expr | None = None
        names: list[str] = []
        if isinstance(node, ast.Assign):
            value = node.value
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            value = node.value
            names = [node.target.id]
        if name in names and value is not None:
            result = ast.literal_eval(value)
            if isinstance(result, str):
                return result
    raise ValueError(f"Could not read literal {name} from {path}")


def expected_fingerprint(repo_root: Path, model_digest: str) -> tuple[str, dict[str, Any]]:
    prompt = _literal_assignment(repo_root / "nova_backend/src/llm/system_prompt.py", "SYSTEM_PROMPT")
    wrapper = (repo_root / "nova_backend/src/llm/inference_wrapper.py").read_text(encoding="utf-8")
    params = {
        "temperature": 0.7,
        "num_predict": NUM_PREDICT,
        "num_ctx": NUM_CTX,
        "top_k": 50,
        "repeat_penalty": 1.1,
        "stop": ["User:", "Human:"],
    }
    blob = json.dumps(
        {
            "model_digest": model_digest,
            "system_prompt": prompt,
            "wrapper": wrapper,
            "params": params,
        },
        sort_keys=True,
    )
    return hashlib.sha256(blob.encode()).hexdigest(), params


def _json_request(url: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _port_open(host: str = "127.0.0.1", port: int = 8000) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex((host, port)) == 0


def _wait_for_backend(timeout: float = 45.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            _json_request("http://127.0.0.1:8000/phase-status")
            return
        except (OSError, urllib.error.URLError, json.JSONDecodeError):
            time.sleep(0.5)
    raise TimeoutError("Nova backend did not become ready before the acceptance timeout.")


def _git_head(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _ollama_digest() -> str:
    payload = _json_request("http://127.0.0.1:11434/api/tags")
    for model in payload.get("models", []):
        if model.get("name") == MODEL:
            digest = str(model.get("digest") or "")
            if len(digest.removeprefix("sha256:")) == 64:
                return digest
    raise RuntimeError(f"Verified digest unavailable for {MODEL}.")


async def _drain_greeting(ws: Any) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=max(0.1, deadline - time.monotonic()))
        except asyncio.TimeoutError:
            return
        payload = json.loads(raw)
        if payload.get("type") == "chat_done":
            return


def _score(prompt_index: int, response: str) -> str:
    lowered = response.lower()
    expected = (
        ("ram", "storage"),
        ("cedar", "tuesday", "pending"),
        ("cedar",),
        ("tuesday",),
        ("pending",),
        ("cedar", "tuesday", "pending"),
    )[prompt_index]
    if all(item in lowered for item in expected):
        return "PASS"
    return "PARTIAL" if response.strip() else "FAIL"


async def _run_turn(ws: Any, prompt: str, prompt_index: int, timeout: float) -> TurnResult:
    result = TurnResult(prompt=prompt)
    samples: list[MemorySample] = []
    done = asyncio.Event()

    async def monitor() -> None:
        while not done.is_set():
            samples.append(memory_sample())
            await asyncio.sleep(0.1)

    monitor_task = asyncio.create_task(monitor())
    started = time.perf_counter()
    first_chat: float | None = None
    messages: list[str] = []
    try:
        await ws.send(json.dumps({"text": prompt, "channel": "text"}))
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
            payload = json.loads(raw)
            kind = str(payload.get("type") or "")
            if kind == "chat":
                if first_chat is None:
                    first_chat = time.perf_counter()
                messages.append(str(payload.get("message") or payload.get("text") or ""))
            elif kind == "error":
                result.error = str(payload.get("message") or payload)
                break
            elif kind == "chat_done":
                break
    except Exception as error:  # evidence must preserve timeouts and connection failures
        result.error = f"{type(error).__name__}: {error}"
    finally:
        done.set()
        await monitor_task

    ended = time.perf_counter()
    result.response = "\n".join(messages).strip()
    result.first_chat_seconds = None if first_chat is None else round(first_chat - started, 3)
    result.total_seconds = round(ended - started, 3)
    if samples:
        result.minimum_available_bytes = min(sample.available_bytes for sample in samples)
        result.maximum_physical_used_percent = max(
            sample.physical_used_percent for sample in samples
        )
    result.score = "FAIL" if result.error else _score(prompt_index, result.response)
    return result


async def _run_conversation(timeout: float, runtime_stop_bytes: int) -> tuple[list[TurnResult], str]:
    turns: list[TurnResult] = []
    stop_reason = "complete"
    async with websockets.connect(
        "ws://127.0.0.1:8000/ws",
        origin="http://localhost:8000",
        open_timeout=10,
        ping_interval=20,
        ping_timeout=20,
        max_size=4 * 1024 * 1024,
    ) as ws:
        await _drain_greeting(ws)
        prompts = (MINIMAL_PROMPT, *CONTEXT_PROMPTS)
        for index, prompt in enumerate(prompts):
            turn = await _run_turn(ws, prompt, index, timeout)
            turns.append(turn)
            safe, reason = runtime_safe(memory_sample(), minimum_available_bytes=runtime_stop_bytes)
            if turn.error or not safe:
                stop_reason = turn.error or reason
                break
    return turns, stop_reason


def _write_evidence(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--expected-digest", required=True)
    parser.add_argument("--confirm-model-update", action="store_true")
    parser.add_argument("--minimum-start-gb", type=float, default=2.0)
    parser.add_argument("--runtime-stop-gb", type=float, default=0.5)
    parser.add_argument("--turn-timeout", type=float, default=120.0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--ollama-executable", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.repo_root.resolve()
    output = args.output or root / "data/acceptance/lightweight_acceptance.json"
    python = root / "nova_backend/venv/Scripts/python.exe"
    if not python.exists():
        raise SystemExit(f"Expected Nova interpreter is missing: {python}")
    if _git_head(root) != args.expected_commit:
        raise SystemExit("Repository HEAD does not match --expected-commit.")
    if _port_open():
        raise SystemExit("Port 8000 is already occupied; refusing to adopt an existing backend.")

    before = memory_sample()
    passed, reason = resource_gate(
        before,
        minimum_available_bytes=int(args.minimum_start_gb * 1024**3),
    )
    evidence: dict[str, Any] = {
        "record_kind": "lightweight_local_acceptance",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "commit": args.expected_commit,
        "profile": {"model": MODEL, "num_ctx": NUM_CTX, "num_predict": NUM_PREDICT},
        "resource_before": asdict(before),
        "preflight": reason,
        "turns": [],
    }
    if not passed:
        evidence["verdict"] = "HOLD"
        _write_evidence(output, evidence)
        print(json.dumps(evidence, indent=2))
        return 2

    environment = os.environ.copy()
    environment.update(
        {
            "OLLAMA_MODEL": MODEL,
            "OLLAMA_NUM_CTX": str(NUM_CTX),
            "OLLAMA_NUM_PREDICT": str(NUM_PREDICT),
            "PYTHONNOUSERSITE": "1",
        }
    )
    backend_started = False
    initially_resident = False
    try:
        subprocess.run(
            [str(python), str(root / "scripts/start_daemon.py"), "--no-browser"],
            cwd=root,
            env=environment,
            check=True,
            timeout=60,
        )
        backend_started = True
        _wait_for_backend()
        residency = _json_request("http://127.0.0.1:11434/api/ps")
        initially_resident = any(
            model.get("name") == MODEL for model in residency.get("models", [])
        )
        digest = _ollama_digest()
        if digest.removeprefix("sha256:") != args.expected_digest.removeprefix("sha256:"):
            raise RuntimeError("Installed model digest does not match --expected-digest.")
        fingerprint, params = expected_fingerprint(root, digest)
        evidence.update({"model_digest": digest, "fingerprint": fingerprint, "params": params})

        status = _json_request("http://127.0.0.1:8000/api/settings/model/status")
        if status.get("inference_blocked"):
            if not args.confirm_model_update:
                raise RuntimeError(
                    "Model confirmation is pending; rerun only with explicit "
                    "--confirm-model-update owner authorization."
                )
            confirmation = _json_request(
                "http://127.0.0.1:8000/api/settings/model/confirm",
                method="POST",
            )
            if not confirmation.get("confirmed"):
                raise RuntimeError("Supported model confirmation did not succeed.")
        lock = root / "nova_backend/src/models/current_model_hash.txt"
        if not lock.exists() or lock.read_text(encoding="utf-8").strip() != fingerprint:
            raise RuntimeError("Version-lock file does not match the verified fingerprint.")

        turns, stop_reason = asyncio.run(
            _run_conversation(
                args.turn_timeout,
                int(args.runtime_stop_gb * 1024**3),
            )
        )
        evidence["turns"] = [asdict(turn) for turn in turns]
        evidence["stop_reason"] = stop_reason
        evidence["resource_after_turns"] = asdict(memory_sample())
        if stop_reason != "complete":
            evidence["verdict"] = "HOLD"
        elif len(turns) != 6 or any(turn.score == "FAIL" for turn in turns):
            evidence["verdict"] = "FAIL"
        elif any(turn.score == "PARTIAL" for turn in turns):
            evidence["verdict"] = "PARTIAL"
        else:
            evidence["verdict"] = "PASS"
    except Exception as error:
        evidence["verdict"] = "HOLD"
        evidence["error"] = f"{type(error).__name__}: {error}"
    finally:
        if backend_started:
            subprocess.run(
                [str(python), str(root / "scripts/stop_daemon.py")],
                cwd=root,
                env=environment,
                check=False,
                timeout=30,
            )
        if not initially_resident and args.ollama_executable:
            executable = args.ollama_executable.resolve()
            if executable.is_file():
                subprocess.run(
                    [str(executable), "stop", MODEL],
                    check=False,
                    timeout=20,
                )
        evidence["resource_after_cleanup"] = asdict(memory_sample())
        evidence["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        _write_evidence(output, evidence)

    print(json.dumps(evidence, indent=2))
    return 0 if evidence.get("verdict") in {"PASS", "PARTIAL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())

