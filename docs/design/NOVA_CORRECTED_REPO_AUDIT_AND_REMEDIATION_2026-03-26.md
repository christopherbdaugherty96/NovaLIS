# Nova Corrected Repo Audit And Remediation
Updated: 2026-03-26

## Purpose
This packet captures the corrected current-state audit after rechecking the live repository instead of relying on older snapshots alone.

It exists to answer two questions clearly:
- what is still actually wrong in the repo today
- what was already closed and should no longer be treated as an open problem

## Confirmed Still True

### 1. `brain_server.py` remains too large
This is still one of the biggest maintainability risks in the project.

Why it matters:
- too much routing, product-surface glue, and legacy compatibility logic live in one file
- small changes are harder to review safely
- the file makes architectural intent harder to audit than it should be

### 2. Legacy non-execution routing still exists beside governed routing
`brain_server.py` still carries `SkillRegistry` and `confirmation_gate` imports.

Current interpretation:
- governed execution still routes through the Governor path
- the legacy path does not currently create a second execution authority path
- it is still architectural debt and should be simplified away over time

### 3. Dependency/install truth needed correction
The repo had:
- floating dependency versions
- wake-word dependency pulled into the base install even though wake word is not a live runtime surface
- no Unix startup script

### 4. Governance-facing status files were stale
`NovaLIS-Governance/STATUS.md` was still written as if Nova were a Capability-16-only staging runtime.

## Closed Or Reclassified

### Timeout handling
This is no longer dead code.

The runtime now has:
- real timeout wrapping
- memory ceiling enforcement
- CPU ceiling enforcement

Residual nuance:
- timeout shutdown still waits for the worker thread, which avoids orphaned background execution but can still feel sticky if a worker is deeply stuck

### Onboarding, Settings, and help surfaces
These are no longer missing.

They are now live in the product.

### Frontend mirror drift
This is no longer just a manual concern.

There is now:
- a mirror-sync checker
- workflow enforcement for that checker

## Remediation Applied In This Change Set

### Dependency correction
- created canonical pinned base requirements at `nova_backend/requirements.txt`
- kept compatibility shim at `nova_backend/src/requirements.txt`
- split wake word into `nova_backend/requirements-optional-wakeword.txt`
- removed unused base dependencies that were not referenced in runtime code:
  - `feedparser`
  - `beautifulsoup4`

### Startup parity
- added `start_nova.sh`
- added `stop_nova.sh`

This gives Nova a documented startup path on macOS/Linux instead of a Windows-only operator story.

### Governance truth correction
- rewrote `NovaLIS-Governance/STATUS.md` to match the current runtime
- rewrote `NovaLIS-Governance/README.md` so new readers are pointed to current runtime truth first
- reclassified `NovaLIS-Governance/RUNTIME_TRUTH.md` as a historical mechanical snapshot instead of a current canonical runtime status source

### Documentation correction
- added a setup/startup guide for local operators
- updated human-facing references so wake word is clearly planned, optional, and not part of the default install

## What Still Remains After This Pass

### 1. `brain_server.py` decomposition
This is still the biggest structural cleanup item.

Best decomposition targets:
- websocket/session handling
- page/widget API surfaces
- governed invocation helpers
- workspace/trust/memory UI payload builders
- bridge/settings endpoints

### 2. Legacy routing cleanup
The legacy conversational path should be reduced so the runtime entrypoint better matches Nova's declared architecture.

### 3. Full provider/connector setup
Settings is now actionable for runtime permissions, but full provider and connector linking still belongs to later work.

### 4. Final real-device TTS confidence
The code path is better than before, but real-device spoken-output confidence is still a separate last-mile validation task.

## Short Version
The repo is in a better state after this pass because:
- install truth is cleaner
- wake word no longer pollutes the default dependency path
- startup is no longer Windows-only
- stale governance status files no longer understate the runtime

The biggest remaining problem is not missing capability.

It is still codebase simplification around `brain_server.py` and the legacy routing layer.
