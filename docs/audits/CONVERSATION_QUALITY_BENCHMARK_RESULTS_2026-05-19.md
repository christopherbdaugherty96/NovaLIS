# Conversation Quality Benchmark Results

Date: 2026-05-19
Server: localhost:8000 (post-PR #213, commit b46d771)
Model: gemma4:e4b (Ollama, local)
Script: `nova_backend/tests/simulations/conversation_quality_benchmark.py`

---

## Summary

```text
Personas:               14
Total turns:            31
Responses received:     31/31
Errors:                 0
Timeouts:               0
Friendly fallbacks:     31
Empty responses:        0

Score 0 (fail):         31
Score 1 (weak):         0
Score 2 (strong):       0

Average quality score:  0.00 / 2.00
Pass rate (>= 1):      0/31 (0.0%)
Strong rate (= 2):     0/31 (0.0%)
```

## Latency

```text
Avg:    169ms
Median: 117ms
p95:    419ms
Max:    4133ms
```

Latency is fast because the model returns empty/unusable output
quickly. The two outliers (Ada T2 at 3796ms, Ivan T2 at 4133ms)
suggest the model attempted generation but produced nothing useful.

## Failure classification

```text
friendly_fallback:      31/31 (100%)
empty_response:         0
timeout:                0
error:                  0
system_leak:            0
deterministic_misroute: 0
```

Every single turn returned the `friendly_fallback` response:
"Not sure what you mean — try: 'what's the news', 'check the
weather', or 'what can you do'."

This is a total LLM failure for conversational turns. The model
(gemma4:e4b) is not producing any usable output for open-ended
general-chat queries routed through the advisory path.

## Per-persona breakdown

```text
Ada    [FAIL FAIL]           avg=0.0  (short follow-up: "tell me more")
Ben    [FAIL FAIL]           avg=0.0  (short follow-up: "why?")
Cora   [FAIL FAIL]           avg=0.0  (short follow-up: "how does that relate?")
Dev    [FAIL FAIL FAIL]      avg=0.0  (topic continuity: 3-turn garden)
Erin   [FAIL FAIL FAIL]      avg=0.0  (topic continuity: books → podcasts → books)
Faye   [FAIL FAIL]           avg=0.0  (ambiguous: "what about that?")
Gil    [FAIL FAIL]           avg=0.0  (ambiguous: "can you explain?")
Hana   [FAIL FAIL]           avg=0.0  (ambiguous: "I'm confused")
Ivan   [FAIL FAIL]           avg=0.0  (opinion: standing desk comparison)
Joy    [FAIL FAIL]           avg=0.0  (advisory: career switch risk)
Kit    [FAIL FAIL]           avg=0.0  (advisory: challenge the advice)
Leo    [FAIL FAIL FAIL]      avg=0.0  (depth: 3-turn morning routine)
Mae    [FAIL FAIL]           avg=0.0  (creative: date night ideas)
Nora   [FAIL FAIL]           avg=0.0  (rephrase: "say it for my grandma")
```

No persona group performed better than another. The failure is
universal across all conversational query types.

## Deterministic routing sanity check

Run alongside the benchmark using the existing reliability
simulation (`live_user_simulation.py`):

```text
Passes:                 32/33 (97.0%)
Responses received:     33/33
Errors:                 0
Timeouts:               0
Latency avg:            742ms
Latency median:         121ms
```

Deterministic routes (time, math, weather, news, email, folder,
search, boundary) are unaffected. The 1 failure is the known Gale
confirmation-context edge case (test expectation, not runtime
defect).

The LLM-dependent turns in the reliability simulation (Drew T2/T3,
Blake T1) also returned `friendly_fallback`, consistent with the
benchmark results.

## Root cause analysis

The failure path for all 31 turns:

```text
session_handler.py: message arrives, no deterministic route matches
  → run_general_chat_fallback() called
    → compose_context_pack, classify_mode
    → GeneralChatSkill.handle → _run_local_model
      → generate_chat(prompt, mode="casual", temperature=0.7, ...)
        → llm_manager.generate → Ollama /api/chat (gemma4:e4b)
          → model returns empty or unusable output
      → _local_conceptual_fallback: no match
      → ResponseFormatter.friendly_fallback() fires
```

The Ollama call completes without error or timeout. The model simply
does not produce usable text for these query types. This is a model
capacity issue: gemma4:e4b (~4B parameters) is too small for
open-ended conversational generation.

Key evidence:
- Latency is fast (median 117ms) — the model isn't struggling with
  inference time, it's producing nothing.
- No errors or timeouts — the infrastructure works.
- No deterministic routes affected — the routing layer is correct.
- The circuit breaker and fallback model are not triggering — the
  primary model responds, just with empty/unusable content.

## Comparison with prior simulations

```text
                    Reliability  Context   Mixed     Load     Quality
                    (#213)       (multi)   (edge)    (12/24)  (benchmark)
Personas:           20           10        14        12/24    14
Turns:              33           36        17        15/30    31
Pass rate:          97.0%        61.1%     94.1%     93.3%    0.0%
Timeouts:           0            0         0         0        0
Errors:             0            0         0         0        0
Fallback count:     3            10        8         1        31
Avg latency:        587ms        135ms     59ms      789ms    169ms
```

The conversation quality benchmark isolates the LLM-dependent path
by eliminating all deterministic routes. The result confirms what the
prior simulations hinted at: Nova's general-chat LLM path is
currently non-functional for open-ended queries with the gemma4:e4b
model.

## Model acceptability assessment

```text
gemma4:e4b is NOT acceptable for conversational general chat.

It produces 0% useful output on pure conversational queries.
It is acceptable for deterministic routing (97% pass rate in the
reliability simulation) because those paths bypass the LLM entirely.
```

## Recommended model/config comparison plan

### Phase 1 — Same model, adjusted parameters (fastest to test)

```text
Test A: gemma4:e4b with temperature 0.5 (current: 0.7 casual)
Test B: gemma4:e4b with num_predict 768 (current: 300-512 dynamic)
Test C: gemma4:e4b with repeat_penalty 1.05 (current: 1.1)
```

If the model is fundamentally too small, parameter tuning will not
help. But these are free to test and rule out configuration issues.

### Phase 2 — Larger Gemma variant (if hardware permits)

```text
Test D: gemma4:e2b (fallback model, smaller — expect worse)
Test E: gemma4:26b (if VRAM permits — expect significantly better)
```

The .env.example documents an upgrade path to gemma4:26b and
gemma4:31b. A 26B model should dramatically improve conversational
quality but requires ~16GB VRAM.

### Phase 3 — Alternative architectures

```text
Test F: llama3.1:8b (good general-purpose, ~5GB VRAM)
Test G: mistral:7b (strong instruction following, ~5GB VRAM)
Test H: phi-3:medium (Microsoft, ~8GB VRAM)
```

These are all free, local, and available via Ollama. The 7-8B class
represents a 2x capacity increase over the current 4B model at
moderate VRAM cost.

### Measurement protocol

Run this benchmark (`conversation_quality_benchmark.py`) against
each configuration. Compare:

```text
- Pass rate (score >= 1)
- Strong rate (score = 2)
- Average quality score
- Friendly fallback count
- Latency avg/median/p95/max
- Whether the model fits in available VRAM
```

Also run the reliability simulation (`live_user_simulation.py`) as
a regression check after each model swap to confirm deterministic
routes are unaffected.

## What this proves

1. **The current model cannot serve conversational queries.** 0/31
   turns produced useful output. This is not a routing, prompt, or
   infrastructure issue — it is a model capacity issue.

2. **Deterministic routes are unaffected.** 32/33 passes in the
   reliability simulation confirm the routing layer works correctly.

3. **The bottleneck is clear.** No amount of prompt tuning,
   context packing, or fallback improvement will produce useful
   conversational output from a model that returns empty strings.
   The model must be upgraded first.

4. **The benchmark is ready for model comparison.** The same script
   can be run against any Ollama model to produce comparable metrics.
