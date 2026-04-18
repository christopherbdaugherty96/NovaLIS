# Live Test Checklist — Cap 53: story_tracker_view
Phase 5 of 6 · Priority: Medium (read_only_local)

## Pre-conditions
- [ ] At least one story is being tracked (use cap 52 first)

## Test 1 — Show story
1. Type: `show story AI regulation`
2. ✅ Story timeline or snapshot returned

## Test 2 — Compare stories
1. Type: `compare stories AI regulation and electric vehicles`
2. ✅ Side-by-side or comparative view returned

## Test 3 — Show relationship graph
1. Type: `show story relationship graph`
2. ✅ Graph or map of story relationships returned

## Sign-off
```
python scripts/certify_capability.py live-signoff 53
python scripts/certify_capability.py lock 53
```
