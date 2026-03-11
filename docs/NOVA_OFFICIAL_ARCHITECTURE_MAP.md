# NOVA Official Architecture Map

Status: Authoritative high-level runtime map  
Scope: Current Phase-4 runtime (with Phase-4.2 development surfaces present)

```mermaid
flowchart TD
    U["User (explicit invocation)"] --> UI["Dashboard/UI Layer (Phase 4.5)\nOrb + Formatter + Widgets (non-authoritative)"]
    UI --> BS["brain_server.py\nOrchestration Layer"]

    BS --> GM["GovernorMediator"]
    GM --> GOV["Governor + CapabilityRegistry"]
    GOV --> EB["ExecuteBoundary"]
    EB --> EX["Executors (Phase 4)\nsearch / open / system / tts / report"]
    EX --> LED["Ledger (attempt + result events)"]
    LED --> BS

    BS --> OUT["Structured response / dashboard payload"]
    OUT --> UI

    BS --> CR["Conversation Router"]
    CR --> CP["Cognitive Pipeline (Phase 4.2)\nrole-based analysis\nbuilder / audit / architect / memory / assumption / contradiction / adversarial"]
    CP --> RND["Intelligence Brief Renderer"]
    RND --> OUT

    UI -.->|"Session-visible hydration allowed\nno background autonomy"| BS
    P5["Phase 5 Memory Substrate (gated / future)"] -.->|"Explicit user action\nGovernor mediation required"| GM
```

## Core Rules
- Intelligence does not equal authority.
- Only `brain_server` invokes `GovernorMediator`.
- Only Governor can authorize execution.
- Cognitive pipeline is analysis-only and non-authoritative.
- All network paths are mediated (`NetworkMediator` / `ModelNetworkMediator`).
- Boundary violations fail closed and are ledger-logged.
- UI hydration is session-visible only and non-background.

## Runtime Truth
- Canonical runtime file: `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- Phase-4 proof packet: `docs/PROOFS/Phase-4/PHASE_4_PROOF_PACKET_INDEX.md`
