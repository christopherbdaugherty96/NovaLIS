# Nova – Deep Code-Level Audit & Execution Brief (2026-04-15)

**Status:** FROZEN – TACTICAL COMPANION TO `MASTER_ROADMAP.md`
**Role:** Engineering hotspot map. Guidance for Tier 3 refactors.
**Warning:** Do not use this document to expand Tier 1 scope. Installer first.

---

## Executive Summary

A static analysis of `christopherbdaugherty96/NovaLIS` confirms the strategic
roadmap is directionally correct. There are no hidden architectural flaws. The
friction preventing "product feel" is localized to specific implementation
accretions documented here.

**Grounding caveat:** Line-range citations below were not re-verified during
this pass. Before any Tier 3 extraction work begins, re-locate each target
with a live grep. Do not refactor against a stale line number.

---

## Part 1: Verified Technical Debt

| Issue | Location | Impact on Product |
| :--- | :--- | :--- |
| **Hot-path monolith: brain_server** | `nova_backend/src/brain_server.py` (3571 lines) | Every new HTTP route or intent adds weight to one file; review fatigue is real. |
| **Hot-path monolith: session_handler** | `nova_backend/src/websocket/session_handler.py` (3821 lines) | High regression risk; changes to one lane can break another. |
| **Missing Python packaging** | Root directory has no `pyproject.toml` / `setup.py` | Prevents `pip install`; blocks clean installer creation. |
| **Frontend duplication** | `Nova-Frontend-Dashboard/` vs `nova_backend/static/` | Changes must be made twice; source of UI drift. |
| **Scattered action logic** | `nova_backend/src/actions/` and `nova_backend/src/agents/` | Unclear where to add `send_email_draft` (Tier 2.1). Note: `api/routes/` cited in earlier drafts does **not** exist; API files are flat under `nova_backend/src/api/`. |
| **No module entry point** | `brain_server.py` has no `def main()` and no `if __name__ == "__main__":` block | Blocks the naive `nova-start = "nova_backend.brain_server:main"` pyproject entry; a small `main()` wrapper is a prerequisite to Tier 1.4. |

---

## Part 2: Surgical Refactor Guide (Do Not Execute Until Tier 3)

*Reference only. Ignore until Tier 1 and Tier 2 are complete.*

### 2.1 Candidate Extractions (verify before cutting)

1. **Intent / routing logic from `brain_server.py`**
   - Earlier drafts cited "~L2100-2190" as a hardcoded regex intent router.
     That range was **re-checked and does not contain intent routing** —
     it holds schedule/clock parsing (`_parse_iso_datetime`,
     `_parse_clock_time`, `_compile_atomic_policy_template`). Re-grep for
     the real routing code before extraction. Use a fresh `Grep` for
     request dispatch, not a pinned line range.
   - Benefit once correctly located: reduces `brain_server.py` by roughly
     several hundred lines and isolates the lanes the README diagrams.

2. **Memory service boundary in `session_handler.py`**
   - Extract vector-store interaction and CRUD into a dedicated module.
   - Benefit: enables better error handling and narrower test seams.

3. **Action registry standardization**
   - Pick one canonical path (proposal: `nova_backend/src/actions/governed/`)
     for all new mutation capabilities so Tier 2.1 (`send_email_draft`)
     lands in one predictable place.

### 2.2 Minimal `pyproject.toml` Skeleton (Tier 1.4 Requirement)

Prerequisite: add a `main()` wrapper in `brain_server.py` (or a thin
`nova_backend/__main__.py`) before the entry-point line below will resolve.

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "novalis"
version = "0.1.0"
dependencies = [
    "fastapi",
    "uvicorn",
    # ... (extract from nova_backend/requirements.txt)
]

[project.scripts]
# Requires: def main() in brain_server.py, or adjust target accordingly.
nova-start = "nova_backend.brain_server:main"
```

---

## Part 3: What This Document Does NOT Do

- It does not authorize Tier 3 refactoring before Tier 1 and Tier 2 ship.
- It does not override `MASTER_ROADMAP.md`'s Section 7 exclusions.
- It does not re-open phase folders.

If a refactor appears urgent, re-read `MASTER_ROADMAP.md` Section 8.1.
