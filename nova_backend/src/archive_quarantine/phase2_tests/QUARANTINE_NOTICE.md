# PHASE 2 TEST FILES QUARANTINE

## Purpose
These test files are from Phase 2 and contain patterns that violate Phase 3.5 constitutional requirements.

## Files:
- phase2_manual_tests.py: Contains direct imports of execute_action (Governor bypass)
- phase2_governor_tests.py: Phase 2 governor test patterns

## Constitutional Violations:
1. **Governor Bypass**: Direct execute_action imports outside Governor mediation
2. **Phase Misalignment**: Test patterns assume Phase 2 execution model

## Status:
- NOT imported by any runtime code
- NOT executed in Phase 3.5
- Retained for historical reference only

## Do NOT:
- Import these files in production code
- Use as reference for Phase 3.5+ development
- Remove without constitutional amendment

## Last Audited: 2026-02-04
