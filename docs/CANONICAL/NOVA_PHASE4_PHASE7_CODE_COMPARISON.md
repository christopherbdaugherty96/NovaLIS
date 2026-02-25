# NovaLIS Phase-4 / Phase-7 Design-to-Code Comparison
**Date:** 2026-02-25  
**Scope:** Compare design intent in `docs/design/Phase 4*` and `docs/design/Phase 7` against mechanically reachable runtime code in `nova_backend/src/`.

---

## 1) Outcome in One Paragraph

The codebase currently implements a **Phase-4 staging core** with a real Governor path, but only two governed execution capabilities are live (`16` search, `17` open preset website). Most Phase-4.2/4.5 and nearly all Phase-7 design surfaces (continuous awareness, autonomous operation tiers, multi-agent cognition, durable user memory architecture, house intelligence mode, end-state presence model) are **not implemented in active runtime** and remain design/planning artifacts.

---

## 2) Files Reviewed (All Requested Design Sets)

### Phase 4
- `docs/design/Phase 4/# 🧬 NOVA COMPLETE CONSTITUTIONAL AUDIT.txt`
- `docs/design/Phase 4/# 🧬 NOVA DEEPSEEK FRAMEWORK.txt`
- `docs/design/Phase 4/##phase 4 tree start.txt`
- `docs/design/Phase 4/CONVERSATIONAL MODE.txt`
- `docs/design/Phase 4/DEEP THOUGHT INTEGRATION.txt`
- `docs/design/Phase 4/DEEPSEEK FRAMEWORK.txt`
- `docs/design/Phase 4/DEEPSEEK INTEGRATION.md`
- `docs/design/Phase 4/Four Pillars document.txt`
- `docs/design/Phase 4/GOVERNED_TTS_SPEC.md.txt`
- `docs/design/Phase 4/NOVA MIND ARCHITECTURE WITH DEEPSEEK.txt`
- `docs/design/Phase 4/🧬 NOVA — IDENTITY & PHILOSOPHY.md`

### Phase 4.2
- `docs/design/Phase 4.2/# 🧬 NOVA PHASE 4.2 ROADMAP (Final).txt`
- `docs/design/Phase 4.2/# 🧬 NOVA PHASE 4.2 ROADMAP.txt`
- `docs/design/Phase 4.2/Nova Orthogonal Cognition Stack.txt`
- `docs/design/Phase 4.2/PresenceDoctrine.md v5.txt`
- `docs/design/Phase 4.2/📄 Phase 4.2 Roadmap.txt (corrected.txt`

### Phase 4.5
- `docs/design/Phase 4.5/# Nova Orb.txt`
- `docs/design/Phase 4.5/# Nova UI Framework.txt`
- `docs/design/Phase 4.5/# 🧬 NOVA COMPLETE CONSTITUTIONAL 1.7.txt`
- `docs/design/Phase 4.5/# 🧬 NOVA PHASE 4.5 ROADMAP.txt`
- `docs/design/Phase 4.5/Nova Personal Intelligence Hub Arch.txt`
- `docs/design/Phase 4.5/UI_FRAMEWORK.md.txt`

### Phase 7
- `docs/design/Phase 7/# Deep Review of the Nova Constitut.txt`
- `docs/design/Phase 7/# 🧬 CONSTITUTIONAL AMENDMENT AUTON.txt`
- `docs/design/Phase 7/# 🧬 CONSTITUTIONAL FRAMEWORK LEARN.txt`
- `docs/design/Phase 7/# 🧬 NOVA INTELLIGENCE CAPACITY THE.txt`
- `docs/design/Phase 7/# 🧬 NOVA INTELLIGENCE CAPACITY1.2.txt`
- `docs/design/Phase 7/# 🧬 NOVA MEMORY ARCHITECTURE USER.txt`
- `docs/design/Phase 7/# 🧬 NOVA PHASE 7 ARCHITECTURE.txt`
- `docs/design/Phase 7/# 🧬 NOVA — HOUSE INTELLIGENCE MODE.txt`
- `docs/design/Phase 7/# 🧭 CONSTITUTIONAL INTERPRETATION.txt`
- `docs/design/Phase 7/# 🧭 NOVA AS A GOVERNED INTELLIGENT.txt`
- `docs/design/Phase 7/# 🧭 NOVA END‑STATE VISION.txt`
- `docs/design/Phase 7/# 🧭 THE NATURE OF AUTONOMOUS ACTIO.txt`
- `docs/design/Phase 7/CONTINUOUS AWARENESS & PRESENCE.txt`
- `docs/design/Phase 7/GOVERNED AGENT WITH BUTLER PRESENCE.txt`
- `docs/design/Phase 7/NOVA MULTI-AGENT GOVERNANCE FRAMEWORK.txt`
- `docs/design/Phase 7/NOVA-PI-BUILD-PHASE7.txt`
- `docs/design/Phase 7/ON THE LIMITS OF CONTAINMENT.txt`
- `docs/design/Phase 7/summary audit.txt`
- `docs/design/Phase 7/🧬 NOVA TRUTH — MASTER REFERENCE DO.txt`

---

## 3) Runtime Baseline Used for Comparison

Code comparison baseline:
- Runtime entrypoints: FastAPI + WebSocket + STT router.
- Governed path: `GovernorMediator` → `Governor` → `ExecuteBoundary` / `SingleActionQueue` / executors.
- Active governed capabilities: 16 (search), 17 (open preset website).
- Registry-listed but disabled capabilities: 18, 19, 20, 21, 32, 48.
- Skill layer still active for weather/news/system/general chat.

---

## 4) Design-to-Code Comparison Matrix

| Theme from Phase 4 / 7 Docs | Design Intent (condensed) | Current Code Reality | Match Level |
|---|---|---|---|
| Governor as authority choke point | All executable effects routed through governance spine | Governor exists and gates governed actions with queue, phase gate, and ledger steps | **Implemented (Core)** |
| Explicit invocation for actions | Deterministic user-triggered execution only | Parser recognizes literal `search/look up/research` and `open <name>` | **Implemented (Narrow)** |
| Broader capability surface (Phase 4+) | Additional capabilities beyond search/open (device/media/files/etc.) | IDs exist in registry but are disabled and have no parser or executor branch | **Declared, Not Implemented** |
| Governed TTS / speech governance | Rich governed speech output protocol | Runtime has chat + widget responses and STT ingestion, but no governed TTS execution layer matching spec documents | **Partially Implemented / Divergent** |
| Orb/presence framework (Phase 4.2/4.5) | Presence-aware UI/behavior layer and stronger orb semantics | Frontend orb status exists as descriptive STT state text only; no deeper presence cognition runtime | **UI Stub Only** |
| Continuous awareness / background cognition (Phase 7) | Ongoing awareness, long-running house intelligence behaviors | No background cognition engine or autonomous loop in active code paths | **Not Implemented** |
| Autonomous operation principles (Phase 7) | Governed autonomy tiers and self-directed action policies | Runtime remains request-driven with no autonomous task initiation path | **Not Implemented** |
| Memory architecture (Phase 7) | User/system memory architecture with richer lifecycle | Minimal correction staging + speech state + ledger; no full user-memory subsystem from Phase-7 docs | **Not Implemented (Phase-7 scope)** |
| Multi-agent governance (Phase 7) | Internal multi-agent orchestration under constitutional controls | No multi-agent runtime orchestration in active backend | **Not Implemented** |
| House intelligence / end-state model | Ambient household intelligence mode | Not present in active runtime code | **Not Implemented** |
| Raspberry Pi / deployment profile | Targeted appliance-like deployment | No dedicated Phase-7 Pi orchestration package surfaced in runtime tree | **Not Implemented (as runtime feature)** |

---

## 5) Concrete Gap Register

### G-01 — Phase-4 docs imply wider live execution than code currently provides
- **Observed:** Many design docs discuss expanded execution capability families.
- **Code reality:** Only cap 16 and cap 17 are executable today.
- **Impact:** Risk of operator confusion about what can run now.

### G-02 — Phase-7 autonomy language exceeds current deterministic request/response runtime
- **Observed:** Phase-7 corpus emphasizes autonomous/continuous behavior models.
- **Code reality:** Current runtime executes only on explicit inbound requests.
- **Impact:** Important to treat Phase-7 docs as roadmap/vision, not active behavior contract.

### G-03 — Memory architecture mismatch
- **Observed:** Phase-7 memory docs describe substantial memory layering.
- **Code reality:** Active memory-related behavior is limited (quick correction staging, speech last text, ledger events).
- **Impact:** Memory expectations should be explicitly marked as future-phase in canonical references.

### G-04 — Presence/orb semantics are mostly conceptual beyond frontend status text
- **Observed:** Presence doctrine and orb architecture docs describe richer state and agency semantics.
- **Code reality:** orb status in dashboard reflects STT/UI states (`READY`, `LISTENING`, etc.) and does not drive deep governance behavior.
- **Impact:** Prevents accidental overclaiming of runtime presence capabilities.

---

## 6) Recommended Canonical Positioning

1. Treat this comparison as the operational truth bridge between design corpus and code reality.
2. Keep `docs/canonical/NOVA_CAPABILITY_MASTER.md` as the runtime capability inventory.
3. Mark Phase-7 design files as **non-binding roadmap** unless/until specific code artifacts, tests, and registry states are promoted.
4. For each newly activated capability, require parser mapping + governor route + tests + ledger event coverage before advertising as active.

---

## 7) Suggested Follow-up Work Items

- Add a short “Binding vs Roadmap” banner at the top of major Phase-7 docs.
- Add a compact `docs/canonical/RUNTIME_FEATURE_FLAGS.md` mapping capability IDs to activation state and proof tests.
- Add CI documentation check to ensure future docs referencing “active” capabilities are consistent with `registry.json` and governor routes.

---

## 8) Summary Verdict

- **Implemented now:** limited Phase-4 governed core + existing deterministic utility skill stack.
- **Planned later:** most Phase-4.2/4.5 and almost all Phase-7 architecture themes.
- **Action for operators:** use canonical runtime docs + code path verification for present-tense capability claims.
