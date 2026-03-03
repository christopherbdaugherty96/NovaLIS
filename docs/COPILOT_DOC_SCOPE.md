# COPILOT DOCUMENTATION DIRECTIVE

**Version:** 1.0  
**Date:** 2026-03-03  
**Authority:** Governor-Supreme  
**Status:** ACTIVE — binding for all documentation contributors and automated tools

---

## Scope

This file codifies the documentation directive for NovaLIS. All future contributors and automated tools must operate within these constraints.

### In-scope (permitted):
- Update proof documents to reflect current runtime state.
- Create missing proof documents if required.
- Create or update root-level `README.md`.
- Create or update `docs/COPILOT_DOC_SCOPE.md` as an instruction file.

### Out-of-scope (prohibited):
- Do not modify architecture.
- Do not refactor code.
- Do not rename files.
- Do not rearrange documentation structure.
- Do not alter constitutional language unless it conflicts with current code.

---

## Authority Principle

Documentation must reflect runtime truth exactly as implemented.

**If documentation conflicts with code:**
→ Update documentation to match code.
→ Never modify code to match documentation.

---

## Constitutional Constraints

All documentation updates must preserve:

- **Governor supremacy** — The Governor is the sole authority gate. No documentation may imply or describe any execution surface outside the Governor.
- **Intelligence–Authority split** — Conversation and cognitive modules are advisory only. No documentation may describe them as capable of execution.
- **No autonomy** — No documentation may describe Nova as having proactive, background, or self-initiated behavior.
- **No background cognition** — No documentation may describe persistent or ambient cognitive processes.
- **No execution outside Governor** — All execution references must trace through `Governor.handle_governed_invocation()`.

---

## Documentation Truth Rule

Proof documents exist to verify specific architectural invariants. When updating a proof document:

1. Read the referenced source code before writing.
2. State only what the code demonstrably does.
3. If a gap was previously documented and is now fixed, update the gap section to RESOLVED with code evidence.
4. Never assert properties not verified against the current commit.

---

## Files That Must Never Be Touched by Documentation-Only Work

- Any `.py` file
- Any `.js`, `.css`, `.html` file
- `registry.json`
- Any file under `nova_backend/src/`
- Any file under `nova_backend/tests/`
- Any file under `nova_frontend/`

---

## Amendment Protocol

If this directive itself requires update, a dated amendment must be appended below with the rationale.

---

*This file is the canonical documentation directive for NovaLIS. All documentation work begins here.*
