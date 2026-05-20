# Active TODO - Nova

Last reviewed: 2026-05-19

---

## Current Active Task

```text
Everyday live-session reliability hardening — complete (2026-05-19).
```

Result:

```text
Baseline simulation:   24/32 passes, 7 timeouts (PR #206).
Post-PR #207 rerun:    25/32 passes, 5 timeouts (marginal).
Post-PR #210 rerun:    27/33 passes, 6 timeouts, 0 errors (effective).
Post-PR #213 rerun:    32/33 passes, 0 timeouts, 0 errors (transformative).

Full hardening cycle:
  Passes:   75% → 97% (+22 points)
  Timeouts: 7 → 0 (eliminated)
  Avg:      4381ms → 587ms (-87%)
  p95:      45016ms → 3147ms (-93%)
  Errors:   1 → 0

Merged PRs (in order):
  PR #206 — baseline simulation harness and results
  PR #207 — Ollama wait-serialization mitigation (marginal)
  PR #209 — streaming design doc and post-#207 results
  PR #210 — streaming LLM fallback implementation (effective)
  PR #211 — deterministic routing for math/news/weather
  PR #212 — on_chunk test-fake compatibility fix
  PR #213 — handler ordering: deterministic commands before ambient clarification

Issue #208 tracks the detailed sequence.

Results: docs/audits/LIVE_USER_SIMULATION_RESULTS_2026-05-19.md
Design: docs/status/STREAMING_LLM_FALLBACK_DESIGN_2026-05-19.md
Script: nova_backend/tests/simulations/live_user_simulation.py
Tracker: https://github.com/christopherbdaugherty96/NovaLIS/issues/208
```

Previous completed lane:

```text
Approval-gate certification closeout — certified for current scope (2026-05-19).
Closeout: docs/status/APPROVAL_GATE_CERTIFICATION_CLOSEOUT_2026-05-19.md
capability_locks.json intentionally not modified (separate P1-P5 process).
```

Remaining lower-priority items:

```text
1. Conversation quality lane — model correction verified (2026-05-19).
   ROOT CAUSE CHAIN:
     a. gemma4:e4b OOM → 0/31 friendly_fallback (model never loaded)
     b. gemma2:2b correction → model loads, 1 real response produced
     c. num_ctx=32768 → inference too slow, 17/19 timeouts
   .env corrected to OLLAMA_MODEL=gemma2:2b, OLLAMA_FALLBACK_MODEL=phi3:mini.
   REMAINING: reduce num_ctx to 4096 for small models, then rerun.
   Benchmark: nova_backend/tests/simulations/conversation_quality_benchmark.py
   Results: docs/audits/CONVERSATION_QUALITY_BENCHMARK_RESULTS_2026-05-19.md
   Comparison: docs/audits/CONVERSATION_MODEL_COMPARISON_RESULTS_2026-05-19.md
   Correction: docs/audits/CONVERSATION_MODEL_CORRECTION_RESULTS_2026-05-19.md
2. Gale confirmation-context edge case (test expectation, not runtime defect).
3. Multi-turn context continuity hardening (Issue #214).
   Simulation: 22/36 passes, 0 timeouts. Deterministic routing and
   confirmation safety work in multi-turn sessions. General-chat
   continuity depends on Ollama throughput.
   Results: docs/audits/MULTI_TURN_CONTEXT_SIMULATION_RESULTS_2026-05-19.md
4. Mixed-request edge case simulation complete (Issue #215).
   Simulation: 16/17 passes, 0 timeouts, 0 errors.
   0 hidden authority expansions, 0 hidden email sends,
   0 hidden browser actions. 1 safe-but-unclear boundary-routing
   issue tracked in Issue #215.
   Results: docs/audits/MIXED_REQUEST_EDGE_SIMULATION_RESULTS_2026-05-19.md
5. Concurrent WebSocket load simulation complete.
   12 and 24 simultaneous sessions. 45/45 responses, 0 timeouts,
   0 errors, 0 cross-session contamination, 0 hidden authority
   expansions. 3 marker-only failures (correct "300." answer).
   Results: docs/audits/CONCURRENT_WEBSOCKET_LOAD_SIMULATION_RESULTS_2026-05-19.md
6. Do not expand capabilities or add Shopify/website workflows.
7. Do not reopen the approval-gate lane unless registry truth changes.
```

---

## Recently Completed / Merged

```text
PR #134 — Cap 16 governed_web_search certification locked.
PR #144 — Everyday UX Friction workstream closed.
PR #145 — Work Style Enforcement Lock merged.
PR #146 — Creator-led Shopify/POD future direction merged.
PR #147 — Nova two-domain product direction merged.
PR #148 — Piper-first voice direction merged.
PR #149 — Current status / continuity synchronization merged.
PR #150 — Audit-first safety boundary merged.
PR #152 — Full repo/doc/code alignment audit artifacts merged.
PR #153 — PASS4 OpenClaw freeform-goal inspection merged.
PR #154 — OpenClaw PATCH A-D hardening merged.
PR #156 — Search stopword cleanup merged.
PR #157 — Post-audit continuity/status synchronization merged.
PR #158 — Runtime-doc regeneration TODO tracking merged.
PR #159 — Current priority/status synchronization merged.
PR #167 — Trust Panel MVP receipt surface merged.
PR #169 — Approval gate next-sequence correction merged.
PR #171 — Approval gate focused regression coverage merged.
PR #172 — Approval gate behavioral live-session coverage merged.
PR #175 — Nova basic workflow verification report merged.
PR #176 — Nova basic workflow regression fixes merged.
PR #177 — Baseline CI blocker cleanup merged.
PR #178 — Baseline CI blocker cleanup merged.
PR #179 — Baseline CI blocker cleanup merged.
PR #180 — Frontend mirror sync baseline fix merged.
PR #182 — Obsidian / Second Brain future-planning preserved.
PR #183 — BigPicture / Auralis operating-model future-planning preserved.
PR #184 — .codex-worktrees/ ignored in .gitignore.
PR #186 — Four-pass safe cleanup and approval-gate certification scaffold merged.
PR #187 — Post-PR186 continuity sync merged.
PR #188 — Approval-gate confirmation capability inventory filled.
PR #190 — Ecosystem simulation matrix merged.
PR #191 — Approval gate workflow simulations merged.
PR #192 — Cap 64 operator journey proof scaffold merged.
PR #193 — Cap 22 operator journey proof scaffold merged.
PR #195 — Cap 64 automated evidence capture merged.
PR #196 — Cap 64 live mailto proof and receipt evidence merged.
PR #197 — Duplicate-yes non-double-execution tests merged.
PR #198 — Cap 64 full live checklist evidence and status sync merged.
PR #199 — Certification matrix evidence sync merged.
PR #200 — Cap 22 automated evidence (23 tests) merged.
PR #201 — Cap 22 live proof and receipt evidence merged.
PR #203 — Recovery evidence for Cap 22 and Cap 64 merged.
PR #202 — Continuity docs synced with PRs #198-203.
PR #204 — Certification matrix synced with PRs #201 and #203.
PR #205 — Approval-gate certification closeout merged.
PR #206 — Live-user simulation harness and baseline results merged.
PR #207 — Ollama wait-serialization mitigation merged.
PR #209 — Post-#207 simulation results and streaming design doc merged.
PR #210 — Streaming LLM fallback for advisory general-chat path merged.
PR #211 — Deterministic routing for math/news/weather merged.
PR #212 — on_chunk test-fake compatibility fix merged.
```

---

## Closed / Not Merged

```text
PR #151 — continuity sync branch closed unmerged.
PR #155 — runtime docs regeneration closed unmerged.
```

Generated runtime docs are current as of the latest recorded drift check on PR #185. No regeneration PR is pending unless `python scripts/check_runtime_doc_drift.py` fails again.

---

## Current Open Follow-Ups

### Everyday live-session reliability — COMPLETE

Status:

```text
Complete (2026-05-19). 75% → 97% passes, 7 → 0 timeouts.
PRs #206-#213 merged.
```

Tracker:

```text
Issue #208 — Everyday reliability next steps after live-user simulation
```

### Multi-turn context continuity — EVIDENCE CAPTURED

Status:

```text
Simulation run (2026-05-19). 22/36 passes, 0 timeouts, 0 errors.
Deterministic routing, confirmation safety, and boundary enforcement
work in multi-turn sessions. General-chat continuity depends on
Ollama throughput (same bottleneck as reliability cycle).
```

Tracker:

```text
Issue #214 — Multi-turn context continuity hardening
```

Results:

```text
docs/audits/MULTI_TURN_CONTEXT_SIMULATION_RESULTS_2026-05-19.md
nova_backend/tests/simulations/multi_turn_context_simulation.py
```

### Approval gate wiring — CLOSED OUT

Status:

```text
certified for current registry-confirmation-bound scope (2026-05-19)
```

Closeout:

```text
docs/status/APPROVAL_GATE_CERTIFICATION_CLOSEOUT_2026-05-19.md
```

Result:

```text
All evidence dimensions complete for Cap 22 and Cap 64.
Certification recorded. capability_locks.json not modified.
Per-capability P5/lock decisions remain separate.
```

### #142 — RS-2 capability list truncation

Status:

```text
needs reproduction / not yet confirmed
```

First step:

```text
capture reproducible live-session evidence
```

### #143 — "tell me more" with prior context

Status:

```text
expected behavior correct / missing session-state-aware integration test
```

Scope:

```text
test-only change
```

### Website-preview live-backend validation

Status:

```text
follow-up debt
```

Scope:

```text
live-backend validation only
no runtime authority expansion
```
