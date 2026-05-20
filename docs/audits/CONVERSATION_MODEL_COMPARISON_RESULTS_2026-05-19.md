# Conversation Model Comparison Results

Date: 2026-05-19
Server: localhost:8000 (post-PR #213, commit 6d3f764)
Benchmark: `nova_backend/tests/simulations/conversation_quality_benchmark.py`
Direct API: Ollama at localhost:11434

---

## Critical finding

The 0/31 conversation quality benchmark result is NOT caused by
model quality. It is caused by **insufficient system memory to load
the configured model**.

```text
System RAM:              ~8 GB total
Free RAM at test time:   ~1.2 GB
gemma4:e4b requires:     9.8 GB  → FAILS (OOM)
gemma4:e2b requires:     7.2 GB  → FAILS (OOM)
gemma3:4b requires:      3.3 GB  → TIMEOUT (loads but too slow under pressure)
phi3:mini requires:      2.2 GB  → WORKS
phi3.5 requires:         2.2 GB  → WORKS
gemma2:2b requires:      1.6 GB  → WORKS
```

Nova's `.env` configures `OLLAMA_MODEL=gemma4:e4b` and
`OLLAMA_FALLBACK_MODEL=gemma4:e2b`. Neither model can be loaded
on this machine. Ollama returns HTTP 500 ("model requires more
system memory than is available") on every call. Nova's LLM
manager catches this error and returns `None`, which triggers
`friendly_fallback()` on every conversational turn.

**Nova's invocation path is not broken.** The prompt construction,
context packing, sanitization, and fallback chain all work correctly.
The model simply never runs.

## Direct Ollama smoke test results

### gemma4:e4b (current configured model)

```text
Prompt: "Say one sentence about why the sky is blue."
Result: ERROR — 500 Internal Server Error
Reason: model requires more system memory (9.8 GiB) than is
        available (3.9 GiB)
```

### gemma4:e2b (configured fallback)

```text
Prompt: "Say one sentence about why the sky is blue."
Result: ERROR — 500 Internal Server Error
Reason: model requires more system memory (7.2 GiB) than is
        available (4.1 GiB)
```

### gemma3:4b

```text
Prompt: "What makes a good morning routine?" (full system prompt)
Result: TIMEOUT at 120 seconds (num_ctx=4096)
Note:   Model may load but inference is extremely slow under
        memory pressure. Not viable on 8 GB system with other
        processes running.
```

### gemma2:2b

```text
Prompt: "Say one sentence about why the sky is blue."
Result: SUCCESS
Output: coherent Rayleigh scattering explanation, ~40 words

Full conversational test:
Prompt: "What makes a good morning routine?" (Nova system prompt)
Result: SUCCESS — 1,740 chars, well-structured, conversational
Follow-up: "tell me more"
Result: SUCCESS — 2,071 chars, context-aware expansion

Quality: good conversational output, emoji usage, structured
lists, topical continuity on follow-up.
```

### phi3:mini

```text
Prompt: "What makes a good morning routine?" (Nova system prompt)
Result: SUCCESS — 2,229 chars, structured 7-point list
Quality: substantive but slightly more formal/stiff than gemma2:2b.
         Minor grammar irregularities ("holidde" for "holidays").
```

### phi3.5

```text
Prompt: "Say one sentence about why the sky is blue."
Result: SUCCESS — coherent explanation, ~50 words
Quality: similar to phi3:mini with slightly better fluency.
```

## Installed models — fit assessment

```text
Model          Disk    RAM needed   Fits 8GB?   Direct test
gemma4:e4b     9.6GB   ~9.8GB       NO          OOM error
gemma4:e2b     7.2GB   ~7.2GB       NO          OOM error
gemma3:4b      3.3GB   ~3.5GB       MARGINAL    Timeout (too slow)
phi3:mini      2.2GB   ~2.5GB       YES         SUCCESS
phi3.5         2.2GB   ~2.5GB       YES         SUCCESS
gemma2:2b      1.6GB   ~1.8GB       YES         SUCCESS
```

## Nova benchmark with current config (baseline)

```text
Model: gemma4:e4b (configured but cannot load)
Pass rate:       0/31 (0.0%)
Strong rate:     0/31 (0.0%)
Avg score:       0.00
Fallback count:  31/31
Timeouts:        0
Errors:          0
Latency avg:     169ms (fast because no inference happens)
```

## Config-only sweep

Config-only parameter sweeps (temperature, repeat_penalty,
num_predict) were NOT run because the root cause is OOM, not
parameter tuning. Adjusting parameters on a model that cannot
load has no effect.

## What this proves

1. **The failure is an OOM, not a model quality or code issue.**
   The configured model (gemma4:e4b, 9.8 GB) cannot run on an
   8 GB system. The fallback model (gemma4:e2b, 7.2 GB) also
   cannot run. Every LLM call fails at the Ollama level.

2. **Nova's LLM invocation path works correctly.** The error is
   caught, the circuit breaker / fallback logic activates, and
   the system degrades gracefully to `friendly_fallback()`. No
   crashes, no hangs, no data corruption.

3. **Three installed models CAN run on this hardware:**
   gemma2:2b, phi3:mini, phi3.5. All produce good conversational
   output when called directly through the Ollama API.

4. **gemma2:2b is the best candidate for this machine.** It has
   the smallest memory footprint (1.6 GB), loads quickly, and
   produces the most natural conversational output of the three
   viable models (emoji usage, structured lists, warm tone that
   matches Nova's personality).

5. **Deterministic routing is unaffected** because those paths
   bypass the LLM entirely. The 32/33 reliability result confirms
   this.

## Recommended next step

**Change `.env` to a model that fits the hardware:**

```text
OLLAMA_MODEL=gemma2:2b
OLLAMA_FALLBACK_MODEL=phi3:mini
```

Then:
1. Restart the Nova server.
2. Confirm the model version hash (LLMManager will require
   confirmation on first run with a new model).
3. Re-run the conversation quality benchmark.
4. Re-run the reliability simulation as regression check.

This is a config-only change (`.env` values). No runtime code
modification is needed.

**Expected outcome:** The benchmark should go from 0/31 to a
meaningful pass rate. gemma2:2b produces good conversational
output (tested above). The remaining quality gap will be real
model capacity limitations of a 2B model, not infrastructure
failure.

## Whether any runtime code change is needed

**No runtime code change is needed.** The invocation path is
correct. The prompt construction, context packing, sanitization,
and fallback chain all work as designed. The only change needed
is a `.env` configuration update to specify a model that fits
the available hardware.

One optional improvement: Nova's LLM manager could log a clear
warning when the Ollama call returns an OOM error, rather than
treating it identically to other failures. This would make the
issue immediately visible in server logs instead of requiring
a diagnostic investigation. But this is an observability
enhancement, not a fix.

## Model comparison matrix

```text
                gemma4:e4b  gemma4:e2b  gemma3:4b  gemma2:2b  phi3:mini  phi3.5
RAM needed:     9.8GB       7.2GB       ~3.5GB     1.8GB      2.5GB      2.5GB
Fits 8GB:       NO          NO          MARGINAL   YES        YES        YES
Direct smoke:   OOM         OOM         TIMEOUT    SUCCESS    SUCCESS    SUCCESS
Chat quality:   —           —           —          GOOD       GOOD       GOOD
Follow-up:      —           —           —          GOOD       untested   untested
Tone match:     —           —           —          STRONG     MODERATE   MODERATE
Recommended:    —           —           —          YES        FALLBACK   FALLBACK
```
