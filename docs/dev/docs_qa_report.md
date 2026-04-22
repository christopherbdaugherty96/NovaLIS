# Docs QA Report

Generated during the public-docs cleanup pass.

## Scope

The audit checked Markdown links across the live repository while excluding generated worktree copies under `.claude/`, virtual environments, caches, and Git internals.

## Summary

- Current public entry points were added and verified:
  - `README.md`
  - `QUICKSTART.md`
  - `USE_CASES.md`
  - `docs/INDEX.md`
  - `docs/product/visual_proof.md`
- Product screenshots were captured and linked.
- Runtime truth remains anchored in `docs/current_runtime/`.
- Current high-value docs were patched for stale links and stale capability claims.

## Current-Doc Fixes Applied

- Rebuilt `docs/reference/ARCHITECTURE.md` to remove mojibake, stale hard-coded capability counts, and broken runtime-roadmap links.
- Rebuilt `docs/reference/INTRODUCTION.md` to remove stale external-write language and point users to current runtime truth.
- Fixed a malformed markdown link in `docs/design/IDEAS/TIME_TEST_GOVERNOR_REFERENCE.md` caused by a code-like `](` sequence.
- Replaced an absolute Windows path link in `docs/design/Phase 4.5/NOVA_LOCAL_PROJECT_AND_ASSISTANT_UTILITY_AUDIT_2026-03-20.md` with a relative repo link.

## Remaining Known Issues

The remaining broken links are in archived or verification-era material:

- `docs/archive/phase 3.5/README_verification.md`
- `verification/README_verification.md`

These files point at historical phase artifacts that are no longer present at their original paths. They were not patched in this pass because they are not surfaced as current entry points. If those packets need to become durable references again, either archive them deeper with a warning banner or rewrite their links to current equivalents.

## Recommendation

Keep future public docs linked through `docs/INDEX.md` and generated runtime truth. Avoid copying exact capability counts, active IDs, hashes, or test totals into product-facing docs unless the same commit updates them from a fresh run.
