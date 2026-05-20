# Local LLM Hardware Profiles

Date: 2026-05-20
Status: Active reference document

---

## Current hardware

```text
Samsung Galaxy Book3 360
RAM: 8 GB
GPU: None (Intel integrated, size_vram=0)
CPU: Intel (mobile)
Inference: CPU-only
Ollama installed models: gemma2:2b (1.5 GB), phi3:mini (2.0 GB)
```

## Current default — fast-local (Profile A)

This is the working default for the current laptop.

```text
OLLAMA_MODEL=gemma2:2b
OLLAMA_FALLBACK_MODEL=phi3:mini
OLLAMA_NUM_CTX=2048
OLLAMA_NUM_PREDICT=128
```

Expected behavior:

```text
First-turn latency:  ~19 s
Follow-up latency:   ~10–15 s
Response length:     ~600 chars (short but useful)
Server stability:    Stable (no OOM)
Deterministic routes: Instant (weather, news, time, math)
```

## Quality mode — same hardware (Profile B)

Use when you want richer answers and can tolerate ~30–40 s waits.

```text
OLLAMA_MODEL=gemma2:2b
OLLAMA_FALLBACK_MODEL=phi3:mini
OLLAMA_NUM_CTX=4096
OLLAMA_NUM_PREDICT=256
```

Expected behavior:

```text
First-turn latency:  ~36 s
Follow-up latency:   ~20–30 s
Response length:     ~1100 chars (richer, more context-aware)
Server stability:    Stable (no OOM)
Benchmark:           20.7% pass rate (6/29), 1 STRONG score
```

---

## Future hardware upgrade profiles

### Profile C: 16 GB RAM + discrete GPU

When upgrading to 16 GB RAM with any CUDA/ROCm-capable GPU:

```text
OLLAMA_MODEL=gemma2:2b
OLLAMA_FALLBACK_MODEL=phi3:mini
OLLAMA_NUM_CTX=8192
OLLAMA_NUM_PREDICT=512
```

Setup steps:

```text
1. Install Ollama (if not already present).
2. Run: ollama pull gemma2:2b
3. Run: ollama pull phi3:mini
4. Update nova_backend/.env with the values above.
5. Restart Nova.
6. Verify via: curl http://localhost:11434/api/ps
   — confirm size_vram > 0 (GPU offload active).
```

Expected improvement:

```text
Inference moves from CPU to GPU (10–50× faster).
First-turn latency:  2–5 s
Follow-up latency:   1–3 s
Response quality:    Same model, much more usable interactively.
```

Optional model upgrades with 16 GB:

```text
gemma4:e4b (8.9 GB) — significantly better reasoning
llama3:8b (4.7 GB)  — strong general-purpose alternative
mistral:7b (4.1 GB) — fast, good at conversation
```

### Profile D: 32+ GB RAM + modern GPU (RTX 3060+)

```text
OLLAMA_MODEL=gemma4:e4b
OLLAMA_FALLBACK_MODEL=gemma2:2b
OLLAMA_NUM_CTX=32768
OLLAMA_NUM_PREDICT=512
```

Setup steps:

```text
1. Run: ollama pull gemma4:e4b
2. Run: ollama pull gemma2:2b
3. Update nova_backend/.env with the values above.
4. Restart Nova.
```

Expected improvement:

```text
First-turn latency:  <2 s
Full context window available (32k tokens).
Much deeper reasoning and conversation quality.
Can handle multi-turn context without degradation.
```

Optional larger models:

```text
llama3:70b-q4 (~40 GB) — requires 64 GB RAM, near GPT-4 quality
deepseek-coder:33b     — strong for code-related queries
```

---

## Benchmark reference data

All measured 2026-05-20 on the current 8 GB laptop (CPU-only):

```text
Config                          Time     Output   Tok/s
─────────────────────────────── ──────── ──────── ─────
gemma2:2b ctx=2048 pred=128     18.7 s    627 c   6.8
gemma2:2b ctx=2048 pred=256     36.4 s    724 c   4.4
gemma2:2b ctx=4096 pred=256     36.0 s   1161 c   6.9
gemma2:2b ctx=4096 pred=512     56.6 s   1064 c   4.2
phi3:mini ctx=2048 pred=128     29.8 s    523 c   4.3
phi3:mini ctx=2048 pred=256     79.7 s   1226 c   3.2
phi3:mini ctx=4096 pred=256     52.5 s    879 c   4.1
phi3:mini ctx=4096 pred=512    114.6 s   1763 c   3.7
```

Key takeaways:

```text
1. gemma2:2b is ~2× faster than phi3:mini in every config.
2. num_predict has the largest impact on latency.
3. ctx=2048 vs 4096 has minimal impact on gemma2:2b.
4. GPU would make all configs instant (<5 s).
```

## Conversation quality progression

```text
Stage                           Pass rate   Notes
─────────────────────────────── ─────────── ──────────────────────────
gemma4:e4b (OOM)                0/31 (0%)   Model never loaded
gemma2:2b, ctx=32768            1/19 (5%)   Server crashed at persona 7
gemma2:2b, ctx=4096, pred=512   6/29 (21%)  First STRONG score
gemma2:2b, ctx=4096, pred=256   6/30 (20%)  1 STRONG, 22 timeouts, 1 error
gemma2:2b, ctx=2048, pred=128   not yet     Fast-local, to be verified
```

## What changes with better hardware

```text
Current (8 GB CPU):
  - Deterministic routes work perfectly (weather, time, math, news).
  - LLM conversations work but are slow (19–56 s per response).
  - Benchmark OOM-kills when Ollama + Nova + test run concurrently.

With 16 GB + GPU:
  - LLM conversations become interactive (2–5 s).
  - Can run benchmarks without OOM.
  - Can use larger models for better reasoning.
  - Can increase context window for better multi-turn coherence.

With 32+ GB + GPU:
  - Can run large models (gemma4:e4b, llama3:70b).
  - Full 32k context window.
  - Near-instant responses.
  - Competitive with cloud API quality.
```
