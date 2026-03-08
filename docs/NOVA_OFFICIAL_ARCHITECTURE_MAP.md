# NOVA Official Architecture Map

Status: Authoritative high-level runtime map  
Scope: Current Phase-4 runtime (with Phase-4.2 development surfaces present)

```mermaid
flowchart TD
    U["User (Text / Voice)"] --> UI["Dashboard UI (WebSocket Client)"]
    UI --> BS["Brain Server (`src/brain_server.py`)"]

    BS --> CR["Conversation Layer (`src/conversation/*`)"]
    CR --> GM["GovernorMediator (intent parse + routing)"]

    GM --> GOV["Governor (single authority choke point)"]
    GOV --> REG["CapabilityRegistry (fail-closed enablement)"]
    GOV --> EB["ExecuteBoundary (timeout/memory/CPU/concurrency caps)"]
    GOV --> SAQ["SingleActionQueue (one governed action at a time)"]

    REG --> GOV
    EB --> GOV
    SAQ --> GOV

    GOV --> EX["Executors (`src/executors/*`)"]
    EX --> NM["NetworkMediator (governed external HTTP)"]
    EX --> LMM["LLM Gateway/Manager"]
    LMM --> MNM["ModelNetworkMediator (local model HTTP boundary)"]

    EX --> TTS["Voice Output (TTS)"]
    EX --> OS["Local OS Actions (capability/profile-gated)"]

    GOV --> LED["LedgerWriter (append-only audit log)"]
    NM --> LED
    MNM --> LED
    EX --> LED

    BS --> TS["Trust Status Telemetry Events"]
    TS --> UI

    BS --> RR["Runtime Auditor + Docs Generator"]
    RR --> CRT["`docs/current_runtime/CURRENT_RUNTIME_STATE.md`"]
```

## Core Rules
- Intelligence does not equal authority.
- Only Governor can authorize execution.
- All network paths are mediated (`NetworkMediator` / `ModelNetworkMediator`).
- Boundary violations fail closed and are ledger-logged.
- Conversation layer is non-authorizing.

## Runtime Truth
- Canonical runtime file: `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- Phase-4 proof packet: `docs/PROOFS/Phase-4/PHASE_4_PROOF_PACKET_INDEX.md`
