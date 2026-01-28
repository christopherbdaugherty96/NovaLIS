# Novalis



\# NovaLIS



NovaLIS is a \*\*calm, deterministic, offline-first household control-plane\*\*.  

It executes \*\*only user-initiated capabilities\*\* through a \*\*single Master Governor\*\*, with explicit authority boundaries, strict phase gating, and full inspectability.



This repository represents the \*\*implementation surface\*\* for NovaLIS as defined by the \*\*NOVA v2.0.4 Canonical Truth\*\*.



---



\## Canonical Identity (Non-Negotiable)



\*\*One-Line Truth\*\*



> NovaLIS is a deterministic household control-plane that executes user-initiated capabilities through a single Master Governor, with no autonomy, no background cognition, and full auditability.



\*\*Constitutional Invariants\*\*



\- No autonomy (user → Nova → Governor → action → Nova → user)

\- No background cognition or silent execution

\- Deterministic behavior (same input → same output)

\- Offline-first by default; online only by explicit request

\- Explicit invocation only (no inferred intent)

\- Full inspectability (logs, traces, ledgers, manifests)



If any code or proposal contradicts the above, it is \*\*invalid by definition\*\* unless an explicit governance unlock exists.



---



\## Phase Status (Reality-Aligned)



| Phase | Status | Notes |

|------|-------|------|

| Phase 0–2 | ✅ \*\*Frozen\*\* | Constitutional foundation, deterministic core, governed actions |

| Phase 3 | 🟡 \*\*Core Complete, Acceptance-Gated\*\* | Memory governance + STT transport implemented; verification required |

| Phase 3.5 | 🔄 \*\*Active\*\* | Trust visibility, recovery tooling, interpretive awareness |

| Phase 4 | 🚫 \*\*Blocked\*\* | Governed agent execution (requires Phase 3.5 completion) |

| Phase 4.5 | 🛡️ \*\*Locked \& Inert\*\* | Deep Think (structured analysis) |

| Phase 5–9 | 🧠 \*\*Planned\*\* | Optional, governance-bounded expansions |

| Phase 10+ | 🚫 \*\*Forbidden\*\* | Autonomy or self-initiated behavior |



\*\*Important:\*\*  

Phase progression is enforced as a \*\*hard safety barrier\*\*, not a roadmap suggestion.



---



\## What Exists in This Repository



This repository contains:



\- A \*\*FastAPI + WebSocket backend\*\* implementing the NovaLIS brain

\- A \*\*deterministic skill registry\*\* (system / weather / news)

\- A \*\*memory governance substrate\*\* (locked / active / deferred tiers)

\- A \*\*static dashboard UI\*\* (observer/control surface)

\- \*\*Governance contracts, locks, and acceptance gates\*\*

\- \*\*Recovery and verification tooling\*\*



Large runtime artifacts (models, binaries) are intentionally excluded from version control.



---



\## What This Repository Does \*Not\* Do



NovaLIS explicitly does \*\*not\*\*:



\- Act autonomously or proactively

\- Perform background reasoning or monitoring

\- Infer user intent

\- Adapt behavior based on history or habits

\- Execute actions without explicit invocation

\- Enable governed agent execution (Phase 4 is blocked)

\- Provide “helpful” escalation beyond defined contracts



If a feature requires Nova to \*\*decide, assume, or initiate\*\*, it is \*\*illegal\*\* under the current canon.



---



\## Repository Navigation (Required for Review)



This repository must be reviewed using the deterministic order defined in:



➡ \*\*REPO\_MAP.md\*\*



That document specifies:

\- Canonical governance sources

\- Safe review order for humans and AI

\- Phase-sensitive files

\- Explicit review constraints



Any review or change proposal that ignores `REPO\_MAP.md` is considered \*\*unsafe\*\*.



---



\## Contribution Rules (Binding)



All contributions are governed by:



➡ \*\*CONTRIBUTING.md\*\*



Key rules include:

\- No scope expansion without explicit unlock

\- No refactors that risk behavioral drift

\- No background tasks, telemetry, or adaptive behavior

\- Smallest possible diffs

\- Governance always overrides convenience



If you are unsure whether a change is allowed: \*\*do not implement it\*\*.



---



\## Runtime Dependencies



Runtime dependencies such as STT models or media tools are \*\*installed locally\*\* and excluded from Git.



See:

\- `nova\_backend/tools/README.md`

\- `.gitignore`



This repository is intentionally \*\*not self-contained\*\* at runtime.



---



\## Status Disclaimer



NovaLIS is \*\*acceptance-gated\*\* and \*\*not production-complete\*\*.



Claims of capability are valid \*\*only\*\* where explicitly implemented and verified.  

Specification does not imply availability.



---



\## Canonical References



\- \*\*NOVA v2.0.4 — Synthesized Canonical Truth\*\*

\- \*\*REPO\_MAP.md\*\* — Deterministic repository navigation

\- \*\*CONTRIBUTING.md\*\* — Governance-aligned contribution rules



These documents together define the \*\*single source of truth\*\* for NovaLIS.



---



\_End of README.\_






## Phase Gates

**GOVERNED ACTIONS ARE DISABLED**

Actions such as:
- Opening applications
- File operations
- Email or messaging actions
- Smart-home or system control

remain **structurally blocked** until **Phase 3.5 verification is complete** and the Phase-4 gate is explicitly unlocked.

_End of README._

