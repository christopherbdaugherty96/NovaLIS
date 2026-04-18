# Live Test Checklist — Cap 60: explain_anything
Phase 5 of 6 · Priority: Medium (read_only_local)

## Test 1 — Explain this
1. Open a web page or document
2. Type: `explain this`
3. ✅ Nova captures context and explains what you're looking at

## Test 2 — What am I looking at
1. Type: `what am I looking at`
2. ✅ Nova describes the active window or page

## Test 3 — Help me understand
1. Open an error message or unfamiliar interface
2. Type: `help me understand this`
3. ✅ Nova provides a relevant explanation

## Test 4 — Walk me through this
1. After an explain response, type: `walk me through this`
2. ✅ Nova provides step-by-step guidance

## Sign-off
```
python scripts/certify_capability.py live-signoff 60
python scripts/certify_capability.py lock 60
```
