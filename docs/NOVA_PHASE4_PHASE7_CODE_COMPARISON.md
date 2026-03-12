# NovaLIS Phase-4 / Phase-7 Design-to-Code Comparison
**Date:** 2026-03-03  
**Scope:** Compare design intent in `docs/design/Phase 4/`, `docs/design/Phase 4.2/`, `docs/design/Phase 4.5/`, and `docs/design/Phase 7/` against mechanically reachable runtime code in `nova_backend/src/`.

---

## 1) Outcome in One Paragraph

The codebase currently implements a **Phase-4 staging core** with a real Governor path. Three governed execution capabilities are fully functional (`16` search, `17` open preset website, `18` TTS with a known param wiring issue), four are wired but their executors are stubs or partial (`19` volume, `20` media, `21` brightness -- all response stubs; `32` OS diagnostics -- partial), and two remain disabled (`22`, `48`). Most Phase-4.2/4.5 and nearly all Phase-7 design surfaces (continuous awareness, autonomous operation tiers, multi-agent cognition, durable user memory architecture, house intelligence mode, end-state presence model) are **not implemented in active runtime** and remain design/planning artifacts.

---

## 2) Files Reviewed (All Requested Design Sets)

Review scope was executed at directory level to avoid filename-encoding drift across legacy artifacts.

- `docs/design/Phase 4/`
- `docs/design/Phase 4.2/`
- `docs/design/Phase 4.5/`
- `docs/design/Phase 7/`

Specific files were sampled from each directory and compared against active runtime code paths under `nova_backend/src/`.

---

## 3) Runtime Baseline Used for Comparison

Code comparison baseline:
- Runtime entrypoints: FastAPI + WebSocket + STT router.
- Governed path: `GovernorMediator` -> `Governor` -> `ExecuteBoundary` / `SingleActionQueue` / executors.
- Active governed capabilities (fully functional): 16 (search), 17 (open preset website), 18 (TTS -- wired with known param issue).
- Active governed capabilities (wired stub/partial): 19 (volume -- stub), 20 (media -- stub), 21 (brightness -- stub), 32 (OS diagnostics -- partial).
- Registry-listed but disabled capabilities: 22, 48.
- Skill layer still active for weather/news/system/general chat.

---

## 4) Design-to-Code Comparison Matrix

| Theme from Phase 4 / 7 Docs | Design Intent (condensed) | Current Code Reality | Match Level |
|---|---|---|---|
| Governor as authority choke point | All executable effects routed through governance spine | Governor exists and gates governed actions with queue, phase gate, and ledger steps | **Implemented (Core)** |
| Explicit invocation for actions | Deterministic user-triggered execution only | Parser recognizes literal `search/look up/research`, `open <name>`, `speak that/read that/say it`, `volume up/down/set volume`, `play/pause/resume`, `brightness up/down/set brightness`, `system check/system status` | **Implemented (Broader surface)** |
| Broader capability surface (Phase 4+) | Additional capabilities beyond search/open (device/media/files/etc.) | IDs 19/20/21/32 are registry-enabled with parser and executor wired, but executors are stubs or partial -- no real OS effect. IDs 22/48 disabled with no parser | **Wired (Stub/Partial) for 19/20/21/32; Declared for 22/48** |
| Governed TTS / speech governance | Rich governed speech output protocol | Cap 18 TTS executor exists using `pyttsx3`; full governor pipeline wired; known issue: `GovernorMediator` sends empty params so text must be injected by `brain_server` before OS-level speech is produced | **Implemented (with known defect)** |
| Orb/presence framework (Phase 4.2/4.5) | Presence-aware UI/behavior layer and stronger orb semantics | Frontend orb status exists as descriptive STT state text only; no deeper presence cognition runtime | **UI Stub Only** |
| Continuous awareness / background cognition (Phase 7) | Ongoing awareness, long-running house intelligence behaviors | No background cognition engine or autonomous loop in active code paths | **Not Implemented** |
| Autonomous operation principles (Phase 7) | Governed autonomy tiers and self-directed action policies | Runtime remains request-driven with no autonomous task initiation path | **Not Implemented** |
| Memory architecture (Phase 7) | User/system memory architecture with richer lifecycle | Minimal correction staging + speech state + ledger; no full user-memory subsystem from Phase-7 docs | **Not Implemented (Phase-7 scope)** |
| Multi-agent governance (Phase 7) | Internal multi-agent orchestration under constitutional controls | No multi-agent runtime orchestration in active backend | **Not Implemented** |
| House intelligence / end-state model | Ambient household intelligence mode | Not present in active runtime code | **Not Implemented** |
| Raspberry Pi / deployment profile | Targeted appliance-like deployment | No dedicated Phase-7 Pi orchestration package surfaced in runtime tree | **Not Implemented (as runtime feature)** |

---

## 5) Concrete Gap Register

### G-01 -- Phase-4 docs imply wider live execution than code currently provides
- **Observed:** Many design docs discuss expanded execution capability families.
- **Code reality:** Caps 16 and 17 are fully functional; cap 18 is functional with a known param wiring issue; caps 19/20/21 are wired but executors are stubs with no real OS effect; cap 32 is wired with partial data.
- **Impact:** Risk of operator confusion about what can run now vs what has real OS effect.

### G-02 -- Phase-7 autonomy language exceeds current deterministic request/response runtime
- **Observed:** Phase-7 corpus emphasizes autonomous/continuous behavior models.
- **Code reality:** Current runtime executes only on explicit inbound requests.
- **Impact:** Important to treat Phase-7 docs as roadmap/vision, not active behavior contract.

### G-03 -- Memory architecture mismatch
- **Observed:** Phase-7 memory docs describe substantial memory layering.
- **Code reality:** Active memory-related behavior is limited (quick correction staging, speech last text, ledger events).
- **Impact:** Memory expectations should be explicitly marked as future-phase in canonical references.

### G-04 -- Presence/orb semantics are mostly conceptual beyond frontend status text
- **Observed:** Presence doctrine and orb architecture docs describe richer state and agency semantics.
- **Code reality:** orb status in dashboard reflects STT/UI states (`READY`, `LISTENING`, etc.) and does not drive deep governance behavior.
- **Impact:** Prevents accidental overclaiming of runtime presence capabilities.

### G-05 -- Stub executors present a false success to the user
- **Observed:** Capabilities 19 (volume), 20 (media), 21 (brightness) return `ActionResult.ok(...)` with a success message.
- **Code reality:** The executors perform no OS operation. The user receives a "Volume up." or "Playback started." confirmation but nothing changes on the system.
- **Impact:** Users may believe the system acted when it did not. This is a functional correctness gap that should be resolved before these capabilities are advertised as working.

---

## 6) Recommended Canonical Positioning

1. Treat this comparison as the operational truth bridge between design corpus and code reality.
2. Keep `docs/NOVA_CAPABILITY_MASTER.md` as the runtime capability inventory.
3. Mark Phase-7 design files as **non-binding roadmap** unless/until specific code artifacts, tests, and registry states are promoted.
4. For each newly activated capability, require parser mapping + governor route + tests + ledger event coverage before advertising as active.

---

## 7) Suggested Follow-up Work Items

- Add a short "Binding vs Roadmap" banner at the top of major Phase-7 docs.
- Add a compact `docs/current_runtime/RUNTIME_FINGERPRINT.md` mapping capability IDs to activation state and proof tests.
- Add CI documentation check to ensure future docs referencing "active" capabilities are consistent with `registry.json` and governor routes.

---

## 8) Summary Verdict

- **Implemented now:** limited Phase-4 governed core (caps 16/17 fully functional; cap 18 functional with known param issue; caps 19/20/21 wired stub; cap 32 wired partial) + existing deterministic utility skill stack.
- **Planned later:** most Phase-4.2/4.5 and almost all Phase-7 architecture themes.
- **Action for operators:** use canonical runtime docs + code path verification for present-tense capability claims. Treat "Wired (Stub)" capabilities as pipeline scaffolding, not functional features -- they produce no real OS effect despite returning success responses.

