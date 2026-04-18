# Live Test Checklist — Cap 17: open_website
Phase 5 of 6 · Priority: Medium (reversible_local)

## Test 1 — Named website
1. Type: `open github`
2. ✅ Browser opens GitHub (github.com)

## Test 2 — Full URL phrase
1. Type: `open the website google.com`
2. ✅ Browser opens Google

## Test 3 — Ambiguous name triggers clarification
1. Type: `open X`
2. ✅ Nova asks for clarification — does not crash

## Test 4 — Source index (after a search)
1. Run a search first, get results
2. Type: `open source 1`
3. ✅ First result URL opens in browser

## Sign-off
```
python scripts/certify_capability.py live-signoff 17
python scripts/certify_capability.py lock 17
```
