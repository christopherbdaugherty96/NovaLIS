"""
Multi-turn context continuity simulation for a running Nova instance.

Tests whether Nova remains coherent across longer everyday conversations
with topic continuity, topic shifts, follow-ups, clarifications, and
return-to-prior-topic turns.

This is a test-only simulation — it does not modify runtime behavior.

Usage from nova_backend:
    python -m tests.simulations.multi_turn_context_simulation

Usage from repo root:
    python nova_backend/tests/simulations/multi_turn_context_simulation.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from typing import Any

try:
    import websockets
except ImportError:
    print("Missing dependency: websockets")
    print("Install it in the Nova backend environment, then rerun.")
    sys.exit(1)


DEFAULT_WS_URL = "ws://localhost:8000/ws"
DEFAULT_ORIGIN = "http://localhost:8000"
TURN_TIMEOUT_SECONDS = 45.0
CONNECT_TIMEOUT_SECONDS = 10.0
BATCH_SIZE = 1  # sequential — context continuity requires single-session ordering
INITIAL_DRAIN_TIMEOUT_SECONDS = 3.0

# ---------------------------------------------------------------------------
# Detection markers (same as live_user_simulation)
# ---------------------------------------------------------------------------

CONFIRMATION_MARKERS = (
    "needs confirmation",
    "reply 'yes' to proceed",
    "reply yes/no",
    "reply 'yes' to continue",
    "should i run that action",
    "confirm",
)
DENIAL_MARKERS = (
    "blocked:",
    "cannot",
    "not approved",
    "no authority was granted",
    "cancelled",
    "canceled",
)
CLARIFICATION_MARKERS = (
    "what should i",
    "what situation",
    "could you clarify",
    "what are you asking",
    "can you be more specific",
    "what topic",
    "what do you mean",
    "could you tell me more about what",
)
DETERMINISTIC_ROUTE_MARKERS = (
    # Time — multiple response formats
    "current time",
    "the time is",
    "right now it's",
    "it's ",       # "It's 6:32 PM" format
    " pm",
    " am",
    # Arithmetic — plain number results
    "the answer is",
    "equals",
    "result is",
    ",",           # comma-formatted numbers like "1,800"
    # Weather
    "weather",
    "temperature",
    "forecast",
    "unavailable",  # "Weather is currently unavailable"
    # News
    "headline",
    "news",
    "top stories",
)
FRIENDLY_FALLBACK_MARKER = "not sure what you mean"


@dataclass(frozen=True)
class Persona:
    name: str
    description: str
    messages: list[str]
    expectations: dict[int, tuple[str, ...]] = field(default_factory=dict)


@dataclass
class TurnResult:
    persona: str
    description: str
    turn_index: int
    sent: str
    latency_ms: float = 0.0
    chat_messages: list[str] = field(default_factory=list)
    frame_types: list[str] = field(default_factory=list)
    error: str = ""
    timed_out: bool = False
    expected: tuple[str, ...] = ()

    @property
    def combined_text(self) -> str:
        return "\n".join(self.chat_messages).strip()

    @property
    def got_response(self) -> bool:
        return bool(self.chat_messages)

    @property
    def got_confirmation(self) -> bool:
        lowered = self.combined_text.lower()
        return any(m in lowered for m in CONFIRMATION_MARKERS)

    @property
    def got_denial_or_cancel(self) -> bool:
        lowered = self.combined_text.lower()
        return any(m in lowered for m in DENIAL_MARKERS)

    @property
    def got_clarification(self) -> bool:
        lowered = self.combined_text.lower()
        return any(m in lowered for m in CLARIFICATION_MARKERS)

    @property
    def got_deterministic_route(self) -> bool:
        lowered = self.combined_text.lower()
        return any(m in lowered for m in DETERMINISTIC_ROUTE_MARKERS)

    @property
    def got_friendly_fallback(self) -> bool:
        return FRIENDLY_FALLBACK_MARKER in self.combined_text.lower()

    @property
    def expectation_passed(self) -> bool:
        if self.error or self.timed_out:
            return False
        if not self.expected:
            return self.got_response
        lowered = self.combined_text.lower()
        checks = {
            "response": self.got_response,
            "confirmation": self.got_confirmation,
            "denial_or_cancel": self.got_denial_or_cancel,
            "no_confirmation": not self.got_confirmation,
            "clarification": self.got_clarification,
            "deterministic_route": self.got_deterministic_route,
            "no_fallback": not self.got_friendly_fallback,
            "no_false_confirm": not self.got_confirmation,
        }
        return all(checks.get(item, False) for item in self.expected)


# ---------------------------------------------------------------------------
# Personas — multi-turn context continuity scenarios
# ---------------------------------------------------------------------------

PERSONAS: list[Persona] = [
    # ── 1. Follow-up continuity ──────────────────────────────────────────
    Persona(
        name="Mira",
        description="follow-up continuity: asks about a topic then follows up",
        messages=[
            "what is machine learning in plain English?",
            "tell me more",
            "how does that relate to deep learning?",
            "can you give me a simple example?",
        ],
        expectations={
            0: ("response", "no_fallback"),
            1: ("response", "no_fallback"),
            2: ("response", "no_fallback"),
            3: ("response", "no_fallback"),
        },
    ),
    # ── 2. Topic shift then return ────────────────────────────────────────
    Persona(
        name="Leo",
        description=(
            "topic shift: starts with general chat, shifts to weather, "
            "then returns to original topic"
        ),
        messages=[
            "what are some good habits for staying productive?",
            "weather in Boston",
            "what time is it?",
            "going back to productivity — any tips for staying focused?",
        ],
        expectations={
            0: ("response", "no_fallback"),
            1: ("deterministic_route", "no_fallback"),
            2: ("deterministic_route", "no_fallback"),
            3: ("response", "no_fallback"),
        },
    ),
    # ── 3. Deterministic commands mid-conversation ────────────────────────
    Persona(
        name="Priya",
        description=(
            "deterministic commands interleaved: chat then utility then chat"
        ),
        messages=[
            "hey nova, what can you do?",
            "news",
            "what is 150 times 12?",
            "thanks, now tell me about yourself",
        ],
        expectations={
            0: ("response", "no_fallback"),
            1: ("deterministic_route", "no_fallback"),
            2: ("deterministic_route", "no_fallback"),
            3: ("response", "no_fallback"),
        },
    ),
    # ── 4. Ambiguous follow-ups without prior context ─────────────────────
    Persona(
        name="Ravi",
        description=(
            "ambiguous follow-ups: sends context-free follow-ups that "
            "should trigger clarification, not hallucinated answers"
        ),
        messages=[
            "tell me more",
            "what went wrong?",
            "i'm confused",
        ],
        expectations={
            0: ("clarification",),
            1: ("clarification",),
            2: ("clarification",),
        },
    ),
    # ── 5. Clarification vs confirmation safety ───────────────────────────
    Persona(
        name="Dana",
        description=(
            "clarification vs confirmation: 'yes' after clarification "
            "must not trigger an approval-gated action"
        ),
        messages=[
            "tell me more",
            "yes",
        ],
        expectations={
            0: ("clarification",),
            1: ("response", "no_false_confirm"),
        },
    ),
    # ── 6. Real confirmation flow preserved ───────────────────────────────
    Persona(
        name="Sasha",
        description=(
            "real confirmation: email draft confirmation flow still works "
            "correctly within a multi-turn session"
        ),
        messages=[
            "what time is it?",
            "draft an email to Alex saying the report is ready",
            "yes",
        ],
        expectations={
            0: ("deterministic_route", "no_fallback"),
            1: ("confirmation",),
            2: ("no_confirmation",),
        },
    ),
    # ── 7. Boundary preservation ──────────────────────────────────────────
    Persona(
        name="Kai",
        description=(
            "boundary preservation: normal chat then boundary-pushing "
            "request then normal chat again"
        ),
        messages=[
            "what's the weather?",
            "open my browser and book a flight to Paris for me",
            "ok fine, what is 42 plus 58?",
        ],
        expectations={
            0: ("deterministic_route", "no_fallback"),
            1: ("denial_or_cancel", "no_confirmation"),
            2: ("deterministic_route", "no_fallback"),
        },
    ),
    # ── 8. Long conversation (6 turns) ────────────────────────────────────
    Persona(
        name="Zara",
        description="long conversation: 6-turn session with mixed topics",
        messages=[
            "hi nova",
            "what can you do?",
            "give me the latest news headlines",
            "interesting — what is 99 divided by 3?",
            "weather in Pittsburgh",
            "thanks, that's all for now",
        ],
        expectations={
            0: ("response", "no_fallback"),
            1: ("response", "no_fallback"),
            2: ("deterministic_route", "no_fallback"),
            3: ("deterministic_route", "no_fallback"),
            4: ("deterministic_route", "no_fallback"),
            5: ("response", "no_fallback"),
        },
    ),
    # ── 9. Repeated topic with variation ──────────────────────────────────
    Persona(
        name="Eli",
        description=(
            "repeated topic variation: asks weather twice with different "
            "phrasing to test dedup / freshness"
        ),
        messages=[
            "weather in Boston",
            "what about New York — what's the weather there?",
            "and Pittsburgh?",
        ],
        expectations={
            0: ("deterministic_route", "no_fallback"),
            1: ("response", "no_fallback"),
            2: ("response", "no_fallback"),
        },
    ),
    # ── 10. Terse user with minimal input ─────────────────────────────────
    Persona(
        name="Jude",
        description=(
            "terse user: very short inputs across multiple turns"
        ),
        messages=[
            "hi",
            "help",
            "news",
            "time",
        ],
        expectations={
            0: ("response", "no_fallback"),
            1: ("response", "no_fallback"),
            2: ("deterministic_route", "no_fallback"),
            3: ("deterministic_route", "no_fallback"),
        },
    ),
]


# ---------------------------------------------------------------------------
# WebSocket helpers (shared with live_user_simulation)
# ---------------------------------------------------------------------------

def _preview(text: str, limit: int = 140) -> str:
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _headers(origin: str) -> list[tuple[str, str]]:
    return [
        ("Host", "localhost:8000"),
        ("Origin", origin),
        ("User-Agent", "nova-multi-turn-context-simulation/1.0"),
    ]


async def _connect(ws_url: str, origin: str):
    headers = _headers(origin)
    kwargs = {
        "open_timeout": CONNECT_TIMEOUT_SECONDS,
        "ping_interval": 20,
        "ping_timeout": 20,
        "max_size": 4 * 1024 * 1024,
    }
    try:
        return await websockets.connect(
            ws_url, additional_headers=headers, **kwargs
        )
    except TypeError:
        return await websockets.connect(
            ws_url, extra_headers=headers, **kwargs
        )


async def _receive_turn(ws: Any, result: TurnResult) -> None:
    while True:
        raw = await asyncio.wait_for(
            ws.recv(), timeout=TURN_TIMEOUT_SECONDS
        )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            result.frame_types.append("non_json")
            result.error = f"Non-JSON frame: {_preview(raw)}"
            return

        msg_type = str(payload.get("type") or "").strip()
        result.frame_types.append(msg_type or "unknown")

        if msg_type == "chat":
            result.chat_messages.append(
                str(payload.get("message") or payload.get("text") or "")
            )
        elif msg_type == "error":
            result.error = str(
                payload.get("message") or payload.get("text") or payload
            )
            return
        elif msg_type == "chat_done":
            return


async def _drain_connection_greeting(ws: Any) -> None:
    deadline = time.perf_counter() + INITIAL_DRAIN_TIMEOUT_SECONDS
    while True:
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            return
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
        except asyncio.TimeoutError:
            return
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if str(payload.get("type") or "").strip() == "chat_done":
            return


# ---------------------------------------------------------------------------
# Persona runner — sequential turns on a single WebSocket (context matters)
# ---------------------------------------------------------------------------

async def run_persona(
    persona: Persona, ws_url: str, origin: str
) -> list[TurnResult]:
    results: list[TurnResult] = []
    try:
        async with await _connect(ws_url, origin) as ws:
            await _drain_connection_greeting(ws)
            for index, text in enumerate(persona.messages):
                result = TurnResult(
                    persona=persona.name,
                    description=persona.description,
                    turn_index=index + 1,
                    sent=text,
                    expected=persona.expectations.get(index, ()),
                )
                turn_id = (
                    f"ctx-{persona.name.lower()}-{index + 1}-"
                    f"{time.time_ns()}"
                )
                payload = {
                    "type": "chat",
                    "text": text,
                    "turn_id": turn_id,
                }
                start = time.perf_counter()
                try:
                    await ws.send(json.dumps(payload))
                    await _receive_turn(ws, result)
                except asyncio.TimeoutError:
                    result.timed_out = True
                    result.error = (
                        f"TIMEOUT after {TURN_TIMEOUT_SECONDS:.0f}s"
                    )
                except Exception as exc:
                    result.error = f"{type(exc).__name__}: {exc}"
                finally:
                    result.latency_ms = (
                        (time.perf_counter() - start) * 1000
                    )
                    results.append(result)
                # Small delay between turns — simulates human typing cadence
                await asyncio.sleep(0.3)
    except Exception as exc:
        results.append(
            TurnResult(
                persona=persona.name,
                description=persona.description,
                turn_index=0,
                sent="[connect]",
                error=(
                    f"CONNECTION ERROR: {type(exc).__name__}: {exc}"
                ),
            )
        )
    return results


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _print_turn(result: TurnResult) -> None:
    if result.timed_out:
        status = "TIMEOUT"
    elif result.error:
        status = "ERROR"
    elif result.expectation_passed:
        status = "PASS"
    else:
        status = "FAIL"

    tags = []
    if result.got_confirmation:
        tags.append("confirm")
    if result.got_clarification:
        tags.append("clarify")
    if result.got_deterministic_route:
        tags.append("determ")
    if result.got_friendly_fallback:
        tags.append("fallback")
    tag_str = f" [{','.join(tags)}]" if tags else ""
    expected = (
        f" expected={'+'.join(result.expected)}" if result.expected else ""
    )
    print(
        f"  [{status:7}] {result.persona:<8} T{result.turn_index:<2} "
        f"{result.latency_ms:>7.0f}ms{tag_str}{expected}"
        f" :: {_preview(result.sent, 60)}"
    )
    detail = result.error or _preview(result.combined_text)
    if detail:
        print(f"           -> {detail}")


def _print_summary(results: list[TurnResult], ws_url: str) -> None:
    total = len(results)
    passes = sum(1 for r in results if r.expectation_passed)
    errors = sum(
        1 for r in results if r.error and not r.timed_out
    )
    timeouts = sum(1 for r in results if r.timed_out)
    confirmations = sum(1 for r in results if r.got_confirmation)
    denials = sum(1 for r in results if r.got_denial_or_cancel)
    clarifications = sum(1 for r in results if r.got_clarification)
    deterministic = sum(
        1 for r in results if r.got_deterministic_route
    )
    fallbacks = sum(1 for r in results if r.got_friendly_fallback)
    response_count = sum(1 for r in results if r.got_response)
    false_confirms = sum(
        1
        for r in results
        if "no_false_confirm" in r.expected and r.got_confirmation
    )
    latencies = [
        r.latency_ms
        for r in results
        if r.got_response and not r.timed_out
    ]

    print()
    print("=" * 78)
    print("MULTI-TURN CONTEXT CONTINUITY SIMULATION SUMMARY")
    print("=" * 78)
    print(f"Target:                 {ws_url}")
    print(f"Personas:               {len(PERSONAS)}")
    print(f"Total turns:            {total}")
    print(f"Passes:                 {passes}/{total}")
    print(f"Responses received:     {response_count}/{total}")
    print(f"Errors:                 {errors}")
    print(f"Timeouts:               {timeouts}")
    print()
    print("Context continuity metrics:")
    print(f"  Clarification prompts:    {clarifications}")
    print(f"  Deterministic route hits: {deterministic}")
    print(f"  LLM fallback hits:        {fallbacks}")
    print(f"  Confirmation prompts:     {confirmations}")
    print(f"  Denial/cancel replies:    {denials}")
    print(f"  False confirm approvals:  {false_confirms}")
    if latencies:
        print()
        print("Latency:")
        print(f"  Avg:    {statistics.mean(latencies):.0f}ms")
        print(f"  Median: {statistics.median(latencies):.0f}ms")
        p95_idx = int((len(latencies) - 1) * 0.95)
        print(
            f"  p95:    {sorted(latencies)[p95_idx]:.0f}ms"
        )
        print(f"  Max:    {max(latencies):.0f}ms")

    failed = [r for r in results if not r.expectation_passed]
    if failed:
        print()
        print("Failures / Exceptions")
        for r in failed:
            reason = r.error or "expectation mismatch"
            print(
                f"  - {r.persona} T{r.turn_index}: {reason} "
                f":: {_preview(r.sent, 80)}"
            )

    # Per-persona context continuity breakdown
    print()
    print("Per-persona results:")
    for persona in PERSONAS:
        p_results = [
            r for r in results if r.persona == persona.name
        ]
        p_pass = sum(1 for r in p_results if r.expectation_passed)
        p_total = len(p_results)
        label = "PASS" if p_pass == p_total else "FAIL"
        print(
            f"  [{label}] {persona.name:<8} "
            f"{p_pass}/{p_total} turns  "
            f"({persona.description})"
        )


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

async def run_all(
    ws_url: str, origin: str, batch_size: int
) -> list[TurnResult]:
    all_results: list[TurnResult] = []
    print("=" * 78)
    print("Nova Multi-Turn Context Continuity Simulation")
    print("=" * 78)
    print(f"Target:    {ws_url}")
    print(f"Origin:    {origin}")
    print(f"Personas:  {len(PERSONAS)}")
    total_turns = sum(len(p.messages) for p in PERSONAS)
    print(f"Turns:     {total_turns}")
    print()

    # Run personas sequentially — each persona is a single
    # WebSocket session testing context continuity.
    # Between personas we batch to add some concurrency.
    for batch_start in range(0, len(PERSONAS), batch_size):
        batch = PERSONAS[batch_start: batch_start + batch_size]
        print(
            f"Batch {batch_start // batch_size + 1}: "
            + ", ".join(p.name for p in batch)
        )
        grouped = await asyncio.gather(
            *(run_persona(p, ws_url, origin) for p in batch)
        )
        for persona_results in grouped:
            all_results.extend(persona_results)
            for result in persona_results:
                _print_turn(result)
        print()
        await asyncio.sleep(0.5)

    _print_summary(all_results, ws_url)
    return all_results


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run Nova multi-turn context continuity simulation."
        )
    )
    parser.add_argument("--ws-url", default=DEFAULT_WS_URL)
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument(
        "--batch-size", type=int, default=BATCH_SIZE
    )
    args = parser.parse_args()

    results = asyncio.run(
        run_all(args.ws_url, args.origin, max(1, args.batch_size))
    )
    return 0 if all(r.expectation_passed for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
