\# Senior Architect Do / Do-Not Contract (LOCKED)



This document captures the senior-architect guidance as non-negotiable constraints.



---



\## REQUIRED (Do)

\- Preserve governor model: skills-first routing, explicit permission/confirmation, refusal-safe failures, silence-first behavior.

\- Keep LLM usage strictly bounded: helper only; never router, actor, retry engine, or default path.

\- Maintain event-driven behavior only; no background updates or silent fetches.

\- Enforce phase discipline: Phase-1 freeze → Phase-2 ActionRequest core → UX polish last.

\- Single source of truth for frontend/backend assets; eliminate duplicates.

\- Deterministic News/Weather contracts (whitelist, headlines-only, current weather only).

\- SAL remains fixed-string, text-only, non-LLM.

\- Acceptance tests before new features (stop, confirmation, headline count, silence on failure).

\- If cached headlines are shown: label cached + timestamp; refresh only via explicit user action.



---



\## FORBIDDEN (Do Not)

\- No background refreshes, auto-updates, silent fetches.

\- No anthropomorphic drift, implicit assumptions, or “smart” default summaries.

\- No LLM-driven routing, planning, action inference, or execution.

\- No feature additions before Phase-2 action mode is stable end-to-end.

\- No UI behavior implying system state, intent, or autonomy.

\- No widening scope via convenience features without explicit contracts.



---



\## Risk Flags (Watch These)

\- UI state drifting from backend truth.

\- LLM fallback becoming the easy default.

\- Over-locking implementation details instead of behavior contracts.

\- Feature creep via “small” UX conveniences.



