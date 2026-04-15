# Nova — Roadmap Execution Changelog

Rolling log of completed roadmap tasks. Newest at top. Keep entries short
and cite the commit hash(es) that delivered the work.

---

## 2026-04-15 — Tier 1 foundation work

### Task 1.4 — `pyproject.toml` + CI (DONE)
- Commits: `<pending>` (this change)
- Added root `pyproject.toml` with:
  - `novalis` package, Python ≥ 3.10, dependencies pinned to match
    `nova_backend/requirements.txt`.
  - Console script `nova-start = "src.brain_server:main"`.
  - Optional `[dev]` extras (pytest, pytest-asyncio, ruff).
  - Minimal `ruff` and `pytest` configuration.
- Added `.github/workflows/ci.yml` — lint + pytest on push/PR, plus a
  smoke check that the `nova-start` entry point resolves.
- Verified locally: `pip install -e .` succeeds in existing venv,
  `nova-start.exe` is generated, `from src.brain_server import main`
  resolves to the new wrapper.
- Known gap: clean-venv verification and first CI run on a PR still
  pending (tracked in `NOW.md` §1.4 follow-ups).

### Task 1.4a — `main()` wrapper (DONE)
- Commit: `2105777`
- Appended 20-line `main()` + `if __name__ == "__main__":` guard to
  `nova_backend/src/brain_server.py`. Mirrors the `start_nova.bat/sh`
  invocation (`uvicorn src.brain_server:app` on 127.0.0.1:8000) with
  `NOVA_HOST` / `NOVA_PORT` env-var overrides.
- Unblocks Task 1.4 entry point.

### Task 1.0 — Preflight baseline (DONE)
- Commit: `3e4107a` (MOC refresh only)
- Ran runtime-doc generator; drift produced in `_MOCs/*` was committed
  as a separate refresh (indexed the new roadmap folder).
- Spot-ran `pytest nova_backend/tests/phase45/ -x -q` → 36/36 passed.
- Full backend pytest suite deferred to first CI run.

### Roadmap document corrections (DONE)
- Commit: `2ce9c8f`
- Removed fabricated line-range citation for "intent routing monolith"
  in `DEEP_CODE_AUDIT.md` (lines 2100-2190 hold schedule/clock parsing,
  not routing).
- Dropped reference to non-existent `nova_backend/src/api/routes/`.
- Reframed "26 read-only capabilities" as "20 read + 6 local-device
  controls; zero external writes" across `MasterRoadMap.md`.
- Added realistic cadence envelope (24-32 weeks at 2-4 hrs/week).

---

*Entries above are factual records of shipped work. Do not edit history
in place; append corrections as new dated entries.*
