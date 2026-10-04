"""Structural runtime smoke proof for Nova.

SCOPE — what this proves: the backend app imports, core HTTP routes and the /ws
WebSocket accept connections, the capability registry loads, selected capability
properties are present, the Governor refuses a confirm-risk capability without a
confirmation flag and refuses an unknown capability, and model status is readable.

NOT PROVEN here (do not read a PASS as comprehensive runtime truth): that a prompt
yields a valid response, that inference or deterministic routing works, that the
model lock prevents inference, that confirmation authorizes only the intended
bounded effect, that receipts/ledger events persist, that live providers return
usable results, or that the Daily Brief is meaningful. Those need dedicated proofs.

This is a structural smoke proof, not an authorization-integrity or end-to-end proof.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "nova_backend"


def _ensure_import_path() -> None:
    backend_path = str(BACKEND)
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)


class ProofRun:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def pass_(self, message: str) -> None:
        print(f"PASS: {message}")

    def info(self, message: str) -> None:
        print(f"INFO: {message}")

    def fail(self, message: str) -> None:
        self.failures.append(message)
        print(f"FAIL: {message}")

    def check(self, message: str, fn: Callable[[], object]) -> object | None:
        try:
            result = fn()
        except Exception as exc:
            self.fail(f"{message} ({type(exc).__name__}: {exc})")
            return None
        self.pass_(message)
        return result

    def require(self, condition: bool, message: str, detail: str = "") -> None:
        if condition:
            self.pass_(message)
            return
        suffix = f" ({detail})" if detail else ""
        self.fail(f"{message}{suffix}")

    def finish(self) -> int:
        print("SCOPE: structural runtime smoke proof only — not comprehensive runtime truth")
        if self.failures:
            print(f"SUMMARY: FAIL ({len(self.failures)} failure(s))")
            return 1
        print("SUMMARY: PASS")
        return 0


def main() -> int:
    proof = ProofRun()
    logging.disable(logging.CRITICAL)
    _ensure_import_path()
    print("Nova structural runtime smoke proof (see module docstring for scope and non-goals)")

    def import_app():
        from src.brain_server import app

        return app

    app = proof.check("backend app imports", import_app)
    if app is None:
        return proof.finish()

    try:
        from fastapi.testclient import TestClient
    except Exception as exc:
        proof.fail(f"FastAPI TestClient imports ({type(exc).__name__}: {exc})")
        return proof.finish()

    client = TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
        raise_server_exceptions=False,
    )

    root = proof.check("dashboard root returns 200", lambda: client.get("/"))
    if root is not None:
        proof.require(getattr(root, "status_code", None) == 200, "dashboard root status is 200", f"status={getattr(root, 'status_code', None)}")

    phase = proof.check("phase-status route returns 200", lambda: client.get("/phase-status"))
    if phase is not None:
        proof.require(getattr(phase, "status_code", None) == 200, "phase-status status is 200", f"status={getattr(phase, 'status_code', None)}")

    def websocket_connects() -> None:
        with client.websocket_connect(
            "/ws",
            headers={"Host": "127.0.0.1", "Origin": "http://127.0.0.1"},
        ):
            return None

    proof.check("websocket /ws accepts a connection", websocket_connects)

    def load_registry():
        from src.governor.capability_registry import CapabilityRegistry

        return CapabilityRegistry()

    registry = proof.check("capability registry loads", load_registry)
    if registry is not None:
        caps = registry.all_capabilities()
        active_enabled = [cap for cap in caps if cap.status == "active" and cap.enabled]
        proof.require(bool(active_enabled), "capability registry loads active capabilities", f"active_enabled={len(active_enabled)}")

        cap16 = registry.get(16)
        proof.require(
            cap16.name == "governed_web_search" and registry.is_enabled(16),
            "cap 16 governed_web_search is active/enabled",
            f"name={cap16.name!r}, enabled={registry.is_enabled(16)}",
        )

        cap64 = registry.get(64)
        proof.require(
            cap64.name == "send_email_draft" and cap64.requires_confirmation and cap64.external_effect,
            "cap 64 requires confirmation before external-effect draft",
            (
                f"name={cap64.name!r}, requires_confirmation={cap64.requires_confirmation}, "
                f"external_effect={cap64.external_effect}"
            ),
        )

    def governor_blocks_email_without_confirmation():
        from src.governor.governor import Governor

        result = Governor().handle_governed_invocation(
            64,
            {
                "to": "test@example.com",
                "subject": "Proof check",
                "body": "This should not execute without confirmation.",
            },
        )
        return result

    cap64_result = proof.check("Governor evaluates cap 64 without confirmation", governor_blocks_email_without_confirmation)
    if cap64_result is not None:
        proof.require(
            cap64_result.success is False
            and str(cap64_result.status) == "refused"
            and "confirmation" in str(cap64_result.message).lower(),
            "Governor blocks cap 64 without confirmation",
            f"success={cap64_result.success}, status={cap64_result.status!r}, message={cap64_result.message!r}",
        )

    def governor_blocks_unknown_capability():
        from src.governor.governor import Governor

        return Governor().handle_governed_invocation(999999, {})

    unknown_result = proof.check("Governor evaluates unknown capability", governor_blocks_unknown_capability)
    if unknown_result is not None:
        proof.require(
            unknown_result.success is False and "unknown capability" in str(unknown_result.message).lower(),
            "Governor blocks unknown capability",
            f"success={unknown_result.success}, message={unknown_result.message!r}",
        )

    def model_status():
        from src.llm.llm_gateway import model_status_snapshot

        return model_status_snapshot()

    status = proof.check("model trust/status snapshot is readable", model_status)
    if isinstance(status, dict):
        compact = {
            "inference_blocked": bool(status.get("inference_blocked")),
            "active_model": status.get("active_model"),
            "expected_fingerprint": status.get("expected_fingerprint"),
            "current_fingerprint": status.get("current_fingerprint"),
        }
        proof.info("model status " + json.dumps(compact, sort_keys=True, default=str))

    return proof.finish()


if __name__ == "__main__":
    raise SystemExit(main())
