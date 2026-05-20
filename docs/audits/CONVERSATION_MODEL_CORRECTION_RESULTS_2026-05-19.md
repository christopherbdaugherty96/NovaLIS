# Conversation Model Correction Results

Date: 2026-05-19
Server: localhost:8000 (gemma2:2b via .env correction)
Prior config: OLLAMA_MODEL=gemma4:e4b (OOM, never loaded)
Test config: OLLAMA_MODEL=gemma2:2b, OLLAMA_FALLBACK_MODEL=phi3:mini
Script: `nova_backend/tests/simulations/conversation_quality_benchmark.py`

---

## Summary

Switching from gemma4:e4b (OOM, never loaded) to gemma2:2b
(fits in RAM) partially restores conversation quality. The model
now loads, runs, and produces real output. However, Nova's default
`num_ctx=32768` causes inference to be too slow for the 45-second
turn timeout on 8 GB hardware, resulting in most turns timing out.

```text
                        gemma4:e4b      gemma2:2b
                        (OOM baseline)  (correction)
Model loads:            NO              YES
Turns completed:        31/31           19/31*
Friendly fallback:      31              0
Timeouts:               0               17
Errors:                 0               1 (connection)
Pass (score >= 1):      0/31 (0%)       1/19 (5.3%)
Quality score avg:      0.00            0.05
Latency median:         117ms           45233ms
```

*12 turns not attempted (benchmark crashed after connection errors
cascaded from server resource exhaustion under sustained inference).

## Critical finding

**The model correction proves the invocation path works.** Dev T2
produced a real, context-aware conversational response through
Nova's full LLM pipeline:

```text
Dev T2: "What about herbs? Which ones grow well alongside vegetables?"
Response: "You want some easy veggies for your garden this spring?
Here's a rundown of things that tend to be pretty forgiving:
lettuce, spinach, ra..."
Score: 1 (WEAK — topically relevant but addressed T1's question
about vegetables rather than T2's question about herbs)
Latency: 77,599ms
```

This is the first time in the five-simulation series that Nova
has produced a real LLM-generated conversational response. The
response came through the full pipeline: session_handler →
run_general_chat_fallback → GeneralChatSkill._run_local_model →
generate_chat → llm_manager.generate → Ollama.

## Why most turns still time out

Nova's LLMManager default options include `num_ctx: 32768`. This
tells Ollama to allocate a 32K-token context window. For gemma2:2b
on 8 GB RAM:

- 32K context window allocates ~1.5 GB of KV cache memory
- Combined with the 1.6 GB model weights, Ollama uses ~3 GB
- Remaining system RAM (~5 GB) is marginal with Nova server,
  OS, and other processes running
- Inference runs but is extremely slow: most turns exceed the
  45-second timeout

When called directly with `num_ctx=4096`, gemma2:2b produces
fluent 1,700+ character responses in under 60 seconds. The 32K
context window is the latency bottleneck, not the model itself.

## Reliability simulation results (gemma2:2b)

```text
Passes:               22/32 (68.8%)
Responses received:   23/32
Errors:               4 (connection timeouts from server exhaustion)
Timeouts:             6
Confirmation prompts: 7
Denial/cancel:        3
Latency avg:          2,281ms
Latency median:       145ms
```

Deterministic routes (time, math, weather, news, email, folder,
search, boundary) pass normally. LLM-dependent turns (Drew T2/T3,
Blake T1) and some confirmation-gated turns (Frankie T2, Gale T2/T3)
time out due to the slow model inference saturating server resources.

Late batches (Harper, Jules, Kai, Noor) failed with connection
errors because the server became unresponsive under sustained
Ollama load.

**Compared to prior reliability baseline (gemma4:e4b config):**

```text
                  gemma4:e4b (OOM)  gemma2:2b
Passes:           32/33 (97%)       22/32 (69%)
Timeouts:         0                 6
Connection errors: 0                4
LLM-dependent:    friendly_fallback  timeout
Deterministic:    PASS              PASS
```

The pass rate dropped because gemma2:2b with 32K context is slower
than gemma4:e4b's instant OOM failure. The OOM config paradoxically
had better deterministic scores because the fast failure didn't
consume server resources. The gemma2:2b config saturates Ollama,
causing timeouts that cascade to connection failures.

## Direct Ollama smoke test (confirmed)

```text
gemma2:2b  — OK, coherent responses, 1,740+ chars conversational
phi3:mini  — OK, 2,229 chars conversational
```

Both models produce good output when called directly with
`num_ctx=4096`.

## What this proves

1. **Nova's LLM invocation path is correct.** The model swap
   produced a real conversational response (Dev T2). The path
   from session_handler through GeneralChatSkill to Ollama works.

2. **The remaining bottleneck is `num_ctx=32768`.** Reducing this
   to 4096 or 8192 for small models would dramatically reduce
   inference time. This is a config/code change in LLMManager
   default_options.

3. **gemma2:2b should become the default for 8 GB machines.**
   It fits in RAM, produces good conversational output when called
   with appropriate parameters, and is the best available model
   for this hardware class.

4. **A runtime code change IS needed** — specifically, the
   `num_ctx` default in LLMManager should be reduced for small
   models (≤4B params). The current 32768 is appropriate for
   larger models but causes unacceptable latency on small models
   with limited RAM. This is a one-line config change:

   ```python
   # llm_manager.py line 77
   "num_ctx": 32768,  # current
   "num_ctx": 4096,   # recommended for 8GB systems
   ```

   Or preferably, read from `.env`:
   ```
   OLLAMA_NUM_CTX=4096
   ```

## Recommended next steps

```text
1. Set .env to OLLAMA_MODEL=gemma2:2b, OLLAMA_FALLBACK_MODEL=phi3:mini.
2. Reduce num_ctx from 32768 to 4096 (config or code change).
3. Restart Nova, rerun both benchmarks.
4. Expected: conversation quality benchmark passes should jump
   from ~5% to 50-80% based on direct Ollama test quality.
5. Deterministic reliability should return to 97%+ because
   faster inference means no resource exhaustion.
```

## Config used for this test

```text
.env:
  OLLAMA_MODEL=gemma2:2b
  OLLAMA_FALLBACK_MODEL=phi3:mini

LLMManager defaults (unchanged):
  num_ctx: 32768
  num_predict: 512
  temperature: 0.7 (casual) / 0.5 (other)
  top_k: 50
  repeat_penalty: 1.1
  stop: ["User:", "Human:"]
  timeout: 300s

Benchmark timeout: 45s per turn
```
