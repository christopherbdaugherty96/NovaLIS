"""
Conversation quality benchmark for Nova's local/free LLM-dependent path.

This benchmark measures Nova's advisory/general-chat conversational
quality. It deliberately avoids deterministic routes (weather, news,
time, math, email, folder) and focuses on the LLM-dependent code path
where the current model (gemma4:e4b) is weakest.

Every persona sends multi-turn conversational exchanges that require
the model to understand context, follow up, and produce original text.
Each response is scored 0-2:
    0 = fail: friendly_fallback, empty, irrelevant, or error
    1 = weak: somewhat relevant but shallow, repetitive, or off-tone
    2 = strong: useful, context-aware, and conversationally natural

The benchmark is test-only and does not modify runtime behavior.

Usage from nova_backend:
    python -m tests.simulations.conversation_quality_benchmark

Usage from repo root:
    python nova_backend/tests/simulations/conversation_quality_benchmark.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Optional

try:
    import websockets
except ImportError:
    print("Missing dependency: websockets")
    print("Install it in the Nova backend environment, then rerun this script.")
    sys.exit(1)


DEFAULT_WS_URL = "ws://localhost:8000/ws"
DEFAULT_ORIGIN = "http://localhost:8000"
TURN_TIMEOUT_SECONDS = 45.0
CONNECT_TIMEOUT_SECONDS = 10.0
BATCH_SIZE = 1  # sequential — context continuity requires single-session ordering
INITIAL_DRAIN_TIMEOUT_SECONDS = 3.0


# ── Detection markers ────────────────────────────────────────────────

FRIENDLY_FALLBACK_MARKERS = (
    "not sure what you mean",
    "not quite sure what you mean",
    "try:",
    "i didn't quite get that",
    "here's what i can help with",
    "i'm not sure how to help with that",
)

DETERMINISTIC_ROUTE_MARKERS = (
    "°f",
    "°c",
    "headlines",
    "breaking",
    "the time is",
    "current time",
    "it's ",
    " pm",
    " am",
    "the answer is",
    "equals",
    "result is",
)

EMPTY_OR_GENERIC_MARKERS = (
    "hello! how can i help",
    "hi! what can i do",
    "hey! what would you like",
    "hi there!",
    "hello there!",
)

# Markers indicating the model echoed the system prompt or personality
# description instead of answering the question.
SYSTEM_LEAK_MARKERS = (
    "i am nova",
    "i'm nova, a friendly",
    "as your personal assistant",
    "as an ai",
    "as a language model",
)


# ── Persona and turn definitions ─────────────────────────────────────

@dataclass(frozen=True)
class ConversationPersona:
    """A test persona with multi-turn conversational exchanges."""
    name: str
    description: str
    messages: list[str]
    # Per-turn hints for the scorer about what a good response looks like.
    # Keys are 0-based turn indices.
    quality_hints: dict[int, str] = field(default_factory=dict)


PERSONAS: list[ConversationPersona] = [
    # ── Group 1: Short follow-ups ────────────────────────────────
    ConversationPersona(
        name="Ada",
        description="introduces a topic, then asks 'tell me more'",
        messages=[
            "I've been thinking about getting into woodworking as a hobby. "
            "What are the basics I should know?",
            "tell me more",
        ],
        quality_hints={
            0: "should explain woodworking basics (tools, materials, safety)",
            1: "should expand on the previous answer, not repeat or fallback",
        },
    ),
    ConversationPersona(
        name="Ben",
        description="asks a question, then asks 'why?'",
        messages=[
            "Is it better to learn Python or JavaScript as a first "
            "programming language?",
            "why?",
        ],
        quality_hints={
            0: "should compare the two languages with reasoning",
            1: "should explain the reasoning behind the recommendation",
        },
    ),
    ConversationPersona(
        name="Cora",
        description="asks a question, then asks 'how does that relate?'",
        messages=[
            "What's the difference between a latte and a cappuccino?",
            "how does that relate to a flat white?",
        ],
        quality_hints={
            0: "should explain the milk/espresso ratio difference",
            1: "should connect flat white to latte/cappuccino comparison",
        },
    ),

    # ── Group 2: Topic continuity ────────────────────────────────
    ConversationPersona(
        name="Dev",
        description="introduces topic, asks follow-up, then returns to original",
        messages=[
            "I'm planning a small vegetable garden this spring. "
            "What vegetables are easiest to grow?",
            "What about herbs? Which ones grow well alongside vegetables?",
            "Going back to the vegetables — when should I plant tomatoes?",
        ],
        quality_hints={
            0: "should list easy vegetables (tomatoes, lettuce, etc.)",
            1: "should suggest companion herbs (basil, mint, etc.)",
            2: "should answer tomato planting timing, referencing the "
               "garden context from turn 1",
        },
    ),
    ConversationPersona(
        name="Erin",
        description="asks about a book topic, drifts, then returns",
        messages=[
            "What are some good books about personal productivity?",
            "Actually, what about podcasts on the same topic?",
            "Let's go back to books. Which one should I start with?",
        ],
        quality_hints={
            0: "should recommend productivity books",
            1: "should pivot to podcast recommendations on productivity",
            2: "should pick one book from the earlier list and explain why",
        },
    ),

    # ── Group 3: Ambiguous conversational turns ──────────────────
    ConversationPersona(
        name="Faye",
        description="uses ambiguous follow-up references",
        messages=[
            "I'm trying to decide between buying a used car and leasing "
            "a new one. What are the trade-offs?",
            "what about that?",
        ],
        quality_hints={
            0: "should compare buying used vs leasing new",
            1: "should attempt to interpret 'that' from context "
               "(ideally ask for clarification or expand on one aspect)",
        },
    ),
    ConversationPersona(
        name="Gil",
        description="says 'can you explain?' after a topic introduction",
        messages=[
            "I heard that compound interest is really important for saving "
            "money. Can you break that down?",
            "can you explain it more simply?",
        ],
        quality_hints={
            0: "should explain compound interest clearly",
            1: "should simplify the explanation from turn 1, "
               "not restart from scratch",
        },
    ),
    ConversationPersona(
        name="Hana",
        description="expresses confusion and asks for help",
        messages=[
            "What's the difference between a 401k and an IRA?",
            "I'm confused about the tax part. Can you explain just that?",
        ],
        quality_hints={
            0: "should compare 401k and IRA",
            1: "should focus specifically on the tax differences, "
               "acknowledging the user's confusion",
        },
    ),

    # ── Group 4: Opinion/advisory style ──────────────────────────
    ConversationPersona(
        name="Ivan",
        description="asks for an opinion comparison",
        messages=[
            "I'm choosing between a standing desk and a regular desk with "
            "an ergonomic chair. What do you think?",
            "which option sounds better for someone who works from home?",
        ],
        quality_hints={
            0: "should compare both options with pros and cons",
            1: "should give a reasoned recommendation for WFH context",
        },
    ),
    ConversationPersona(
        name="Joy",
        description="asks how to think about a decision",
        messages=[
            "I'm thinking about switching careers from accounting to "
            "software development. Is that realistic?",
            "how should I think about the financial risk?",
        ],
        quality_hints={
            0: "should address career switch feasibility",
            1: "should frame the financial risk analysis "
               "(savings runway, income gap, training costs)",
        },
    ),
    ConversationPersona(
        name="Kit",
        description="asks for advice then challenges it",
        messages=[
            "Should I invest in learning Spanish or Mandarin?",
            "But isn't Mandarin way harder? Is it really worth the effort?",
        ],
        quality_hints={
            0: "should compare the two languages for learning value",
            1: "should address the difficulty concern directly, "
               "not just repeat the comparison",
        },
    ),

    # ── Group 5: Conversational depth and nuance ─────────────────
    ConversationPersona(
        name="Leo",
        description="three-turn deepening conversation",
        messages=[
            "What makes a good morning routine?",
            "How long should it take realistically?",
            "What if I only have 15 minutes?",
        ],
        quality_hints={
            0: "should describe components of a good morning routine",
            1: "should give realistic time estimates",
            2: "should adapt the routine to a 15-minute constraint, "
               "referencing the components from turn 1",
        },
    ),
    ConversationPersona(
        name="Mae",
        description="asks a creative/open-ended question, then narrows",
        messages=[
            "What are some unique date night ideas that don't involve "
            "going to a restaurant?",
            "Which of those would work in winter?",
        ],
        quality_hints={
            0: "should suggest creative date ideas (not restaurants)",
            1: "should filter or adapt the suggestions for winter, "
               "referencing the previous list",
        },
    ),
    ConversationPersona(
        name="Nora",
        description="asks for explanation then asks to rephrase",
        messages=[
            "How does blockchain technology actually work?",
            "Can you say that in a way my grandma would understand?",
        ],
        quality_hints={
            0: "should explain blockchain mechanics",
            1: "should dramatically simplify the explanation, "
               "using everyday analogies",
        },
    ),
]


# ── Scoring ──────────────────────────────────────────────────────────

def _score_response(
    text: str,
    turn_index: int,
    persona: ConversationPersona,
    prev_response: Optional[str],
) -> int:
    """
    Score a response 0-2.

    0 = fail: friendly_fallback, empty, irrelevant, system leak, or
        deterministic route when we expected conversation
    1 = weak: got a response that isn't a fallback/leak but is shallow,
        very short, or doesn't clearly relate to the conversation
    2 = strong: useful, context-aware, and conversationally natural

    Scoring is deliberately conservative. Automated scoring can detect
    clear failures (score 0) and clear successes (score 2) but the
    boundary between 1 and 2 requires human judgment. The benchmark
    errs toward score 1 (weak) when uncertain.
    """
    if not text or not text.strip():
        return 0

    lowered = text.lower().strip()

    # Friendly fallback = score 0
    if any(marker in lowered for marker in FRIENDLY_FALLBACK_MARKERS):
        return 0

    # System prompt leak = score 0
    if any(marker in lowered for marker in SYSTEM_LEAK_MARKERS):
        return 0

    # Empty/generic greeting when we asked a real question = score 0
    if (
        turn_index == 0
        and len(lowered) < 80
        and any(marker in lowered for marker in EMPTY_OR_GENERIC_MARKERS)
    ):
        return 0

    # Unexpectedly hit a deterministic route = score 0
    # (this benchmark avoids deterministic triggers, so this means
    # the model misrouted)
    if any(marker in lowered for marker in DETERMINISTIC_ROUTE_MARKERS):
        return 0

    # Very short response on a follow-up turn = likely not useful
    if turn_index > 0 and len(text.strip()) < 30:
        return 0

    # ── Passed the fail filters. Now distinguish 1 vs 2. ─────────

    word_count = len(text.split())

    # Follow-up turn: check if response references prior context.
    # A score-2 follow-up should not be a standalone answer that
    # ignores the conversation history.
    if turn_index > 0 and prev_response:
        # Extract a few content words from the previous response
        # to check for topical continuity.
        prev_words = set(
            w.lower().strip(".,!?;:'\"")
            for w in prev_response.split()
            if len(w) > 4
        )
        current_words = set(
            w.lower().strip(".,!?;:'\"")
            for w in text.split()
            if len(w) > 4
        )
        overlap = prev_words & current_words
        # If there's meaningful word overlap with the previous response,
        # the model is likely tracking context.
        if len(overlap) >= 3 and word_count >= 25:
            return 2
        # Some overlap but short or thin = weak
        if len(overlap) >= 1 and word_count >= 15:
            return 1
        # No overlap at all on a follow-up = weak at best
        if word_count >= 40:
            return 1  # long but disconnected
        return 1  # got something, but not clearly connected

    # First turn: just check if the response is substantive.
    if word_count >= 40:
        return 2
    if word_count >= 15:
        return 1
    return 1  # got a response, but very short


# ── Turn result ──────────────────────────────────────────────────────

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
    quality_score: int = 0
    quality_hint: str = ""
    prev_response: str = ""

    @property
    def combined_text(self) -> str:
        return "\n".join(self.chat_messages).strip()

    @property
    def got_response(self) -> bool:
        return bool(self.chat_messages)

    @property
    def got_friendly_fallback(self) -> bool:
        lowered = self.combined_text.lower()
        return any(marker in lowered for marker in FRIENDLY_FALLBACK_MARKERS)

    @property
    def is_empty_response(self) -> bool:
        return not self.combined_text.strip()

    @property
    def is_pass(self) -> bool:
        """Pass = score >= 1 (any non-fail response)."""
        return self.quality_score >= 1

    @property
    def is_strong_pass(self) -> bool:
        """Strong pass = score 2 (useful and context-aware)."""
        return self.quality_score == 2


# ── WebSocket helpers (same pattern as live_user_simulation.py) ──────

def _preview(text: str, limit: int = 140) -> str:
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _headers(origin: str) -> list[tuple[str, str]]:
    return [
        ("Host", "localhost:8000"),
        ("Origin", origin),
        ("User-Agent", "nova-conversation-quality-benchmark/1.0"),
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
            ws_url, additional_headers=headers, **kwargs,
        )
    except TypeError:
        return await websockets.connect(
            ws_url, extra_headers=headers, **kwargs,
        )


async def _receive_turn(ws: Any, result: TurnResult) -> None:
    while True:
        raw = await asyncio.wait_for(
            ws.recv(), timeout=TURN_TIMEOUT_SECONDS,
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
                str(payload.get("message") or payload.get("text") or ""),
            )
        elif msg_type == "error":
            result.error = str(
                payload.get("message") or payload.get("text") or payload,
            )
            return
        elif msg_type == "chat_done":
            return


async def _drain_connection_greeting(ws: Any) -> None:
    """Discard Nova's automatic connection greeting."""
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


# ── Persona runner ───────────────────────────────────────────────────

async def run_persona(
    persona: ConversationPersona,
    ws_url: str,
    origin: str,
) -> list[TurnResult]:
    results: list[TurnResult] = []
    prev_response = ""
    try:
        async with await _connect(ws_url, origin) as ws:
            await _drain_connection_greeting(ws)
            for index, text in enumerate(persona.messages):
                hint = persona.quality_hints.get(index, "")
                result = TurnResult(
                    persona=persona.name,
                    description=persona.description,
                    turn_index=index + 1,
                    sent=text,
                    quality_hint=hint,
                    prev_response=prev_response,
                )
                turn_id = (
                    f"cqb-{persona.name.lower()}-"
                    f"{index + 1}-{time.time_ns()}"
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

                # Score the response.
                if result.error or result.timed_out:
                    result.quality_score = 0
                else:
                    result.quality_score = _score_response(
                        result.combined_text,
                        index,
                        persona,
                        prev_response,
                    )

                prev_response = result.combined_text
                results.append(result)
                await asyncio.sleep(0.15)
    except Exception as exc:
        results.append(
            TurnResult(
                persona=persona.name,
                description=persona.description,
                turn_index=0,
                sent="[connect]",
                error=f"CONNECTION ERROR: {type(exc).__name__}: {exc}",
            ),
        )
    return results


# ── Output ───────────────────────────────────────────────────────────

SCORE_LABELS = {0: "FAIL", 1: "WEAK", 2: "STRONG"}


def _print_turn(result: TurnResult) -> None:
    if result.timed_out:
        status = "TIMEOUT"
    elif result.error:
        status = "ERROR"
    else:
        status = SCORE_LABELS.get(result.quality_score, "?")

    print(
        f"  [{status:7}] {result.persona:<6} T{result.turn_index:<2} "
        f"{result.latency_ms:>7.0f}ms :: {_preview(result.sent, 68)}"
    )
    detail = result.error or _preview(result.combined_text)
    if detail:
        print(f"           -> {detail}")


def _classify_failures(results: list[TurnResult]) -> dict[str, list[TurnResult]]:
    """Group score-0 results by failure type."""
    categories: dict[str, list[TurnResult]] = {
        "friendly_fallback": [],
        "empty_response": [],
        "timeout": [],
        "error": [],
        "system_leak": [],
        "deterministic_misroute": [],
        "too_short": [],
        "other": [],
    }
    for r in results:
        if r.quality_score != 0:
            continue
        if r.timed_out:
            categories["timeout"].append(r)
        elif r.error:
            categories["error"].append(r)
        elif r.got_friendly_fallback:
            categories["friendly_fallback"].append(r)
        elif r.is_empty_response:
            categories["empty_response"].append(r)
        elif any(
            m in r.combined_text.lower() for m in SYSTEM_LEAK_MARKERS
        ):
            categories["system_leak"].append(r)
        elif any(
            m in r.combined_text.lower()
            for m in DETERMINISTIC_ROUTE_MARKERS
        ):
            categories["deterministic_misroute"].append(r)
        elif r.turn_index > 1 and len(r.combined_text.strip()) < 30:
            categories["too_short"].append(r)
        else:
            categories["other"].append(r)
    return {k: v for k, v in categories.items() if v}


def _print_summary(results: list[TurnResult], ws_url: str) -> None:
    total = len(results)
    passes = sum(1 for r in results if r.is_pass)
    strong = sum(1 for r in results if r.is_strong_pass)
    fails = sum(1 for r in results if r.quality_score == 0)
    weak = sum(1 for r in results if r.quality_score == 1)
    responses = sum(1 for r in results if r.got_response)
    errors = sum(1 for r in results if r.error and not r.timed_out)
    timeouts = sum(1 for r in results if r.timed_out)
    fallbacks = sum(1 for r in results if r.got_friendly_fallback)
    empty = sum(1 for r in results if r.is_empty_response)
    latencies = [
        r.latency_ms for r in results if r.got_response and not r.timed_out
    ]
    scores = [r.quality_score for r in results]

    print()
    print("=" * 78)
    print("CONVERSATION QUALITY BENCHMARK — SUMMARY")
    print("=" * 78)
    print(f"Target:                 {ws_url}")
    print(f"Personas:               {len(PERSONAS)}")
    print(f"Total turns:            {total}")
    print()
    print(f"Responses received:     {responses}/{total}")
    print(f"Errors:                 {errors}")
    print(f"Timeouts:               {timeouts}")
    print(f"Friendly fallbacks:     {fallbacks}")
    print(f"Empty responses:        {empty}")
    print()
    print(f"Score 0 (fail):         {fails}")
    print(f"Score 1 (weak):         {weak}")
    print(f"Score 2 (strong):       {strong}")
    print()
    avg_score = statistics.mean(scores) if scores else 0
    print(f"Average quality score:  {avg_score:.2f} / 2.00")
    print(f"Pass rate (>= 1):      {passes}/{total} "
          f"({100 * passes / total:.1f}%)" if total else "")
    print(f"Strong rate (= 2):     {strong}/{total} "
          f"({100 * strong / total:.1f}%)" if total else "")

    if latencies:
        print()
        print(f"Latency avg:            {statistics.mean(latencies):.0f}ms")
        print(f"Latency median:         "
              f"{statistics.median(latencies):.0f}ms")
        sorted_lat = sorted(latencies)
        p95_idx = int((len(sorted_lat) - 1) * 0.95)
        print(f"Latency p95:            {sorted_lat[p95_idx]:.0f}ms")
        print(f"Latency max:            {max(latencies):.0f}ms")

    # Failure classification
    failures = _classify_failures(results)
    if failures:
        print()
        print("Failure Classification")
        for category, items in failures.items():
            print(f"  {category}: {len(items)}")
            for r in items:
                print(
                    f"    - {r.persona} T{r.turn_index}: "
                    f"{_preview(r.sent, 60)}"
                )
                if r.combined_text.strip():
                    print(f"      -> {_preview(r.combined_text, 80)}")

    # Per-persona breakdown
    print()
    print("Per-Persona Breakdown")
    persona_names = []
    seen = set()
    for r in results:
        if r.persona not in seen:
            persona_names.append(r.persona)
            seen.add(r.persona)
    for name in persona_names:
        persona_results = [r for r in results if r.persona == name]
        scores_str = " ".join(
            SCORE_LABELS.get(r.quality_score, "?")
            for r in persona_results
        )
        avg = statistics.mean(
            r.quality_score for r in persona_results
        )
        desc = persona_results[0].description if persona_results else ""
        print(f"  {name:<6} [{scores_str}] avg={avg:.1f}  ({desc})")


# ── Main ─────────────────────────────────────────────────────────────

async def run_all(
    ws_url: str,
    origin: str,
    batch_size: int,
) -> list[TurnResult]:
    all_results: list[TurnResult] = []
    print("=" * 78)
    print("Nova Conversation Quality Benchmark")
    print("=" * 78)
    print(f"Target:    {ws_url}")
    print(f"Origin:    {origin}")
    print(f"Personas:  {len(PERSONAS)}")
    total_turns = sum(len(p.messages) for p in PERSONAS)
    print(f"Turns:     {total_turns}")
    print()

    for batch_index in range(0, len(PERSONAS), batch_size):
        batch = PERSONAS[batch_index: batch_index + batch_size]
        print(
            f"Persona {batch_index + 1}: "
            + ", ".join(p.name for p in batch)
        )
        grouped = await asyncio.gather(
            *(run_persona(p, ws_url, origin) for p in batch),
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
        description="Run Nova conversation quality benchmark.",
    )
    parser.add_argument("--ws-url", default=DEFAULT_WS_URL)
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help="personas per batch (default 1 for context continuity)",
    )
    args = parser.parse_args()

    results = asyncio.run(
        run_all(args.ws_url, args.origin, max(1, args.batch_size)),
    )
    total = len(results)
    passes = sum(1 for r in results if r.is_pass)
    strong = sum(1 for r in results if r.is_strong_pass)
    scores = [r.quality_score for r in results]
    avg = statistics.mean(scores) if scores else 0
    print()
    print(f"Exit: {passes}/{total} pass, {strong}/{total} strong, "
          f"avg {avg:.2f}")
    return 0 if passes > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
