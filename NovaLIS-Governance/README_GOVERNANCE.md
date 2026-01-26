\# NovaLIS Governance Vault



This folder contains the locked architectural contracts and phase boundaries for NovaLIS.



Purpose:

\- Prevent scope creep

\- Prevent autonomy drift

\- Keep the governor model intact

\- Make future changes deliberate and auditable



Rules:

\- These documents are higher authority than implementation.

\- If code conflicts with a lock, code changes — not the lock — unless explicitly unlocked.

\- Any change to a LOCK file must be intentional and documented (with a reason).



Contents:

\- ARCHITECT\_CONTRACT.md: Constitution (non-negotiable architecture)

\- PRE\_COMMIT\_CHECKLIST.md: The run-every-time checklist before commits

\- REPO\_ANNOTATION\_MAP.md: Which rules apply to which folders/files

\- SENIOR\_REVIEW\_DO\_NOTS.md: The “no excuses” list + risk flags

\- PHASE\_1\_LOCK.md / PHASE\_2\_LOCK.md / PHASE\_3\_LOCK.md: Phase boundaries and allowed scope



