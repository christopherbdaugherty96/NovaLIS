# Live Test Checklist — Cap 16: governed_web_search
Phase 5 of 6 · Priority: Medium (read_only_network)

## Pre-conditions
- [ ] Nova is running
- [ ] A search API key is configured (or Nova falls back gracefully)

## Test 1 — Basic search
1. Type: `search for latest AI news`
2. ✅ Results widget appears with source links
3. ✅ No raw Python errors in the response

## Test 2 — Natural phrasing
1. Type: `look up what is happening with electric vehicles`
2. ✅ Results returned, sources visible

## Test 3 — Clarification flow
1. Type just: `search`
2. ✅ Nova asks "What would you like to search for?" (clarification, not error)

## Test 4 — Ledger
1. Check Trust page
2. ✅ `SEARCH_QUERY` and `ACTION_COMPLETED` events present

## Sign-off
```
python scripts/certify_capability.py live-signoff 16
python scripts/certify_capability.py lock 16
```
