# Live Test Checklist — Cap 51: topic_memory_map
Phase 5 of 6 · Priority: Medium (read_only_local)

## Pre-conditions
- [ ] Some headlines have been loaded (run `news` or load the news page first)

## Test 1 — Show topic map
1. Type: `show topic map`
2. ✅ Topic map widget returns
3. ✅ Shows recurring themes from current headline set
4. ✅ No crash if no headlines are loaded — graceful "no data" message

## Test 2 — Alternative trigger
1. Type: `open topic memory map`
2. ✅ Same result

## Sign-off
```
python scripts/certify_capability.py live-signoff 51
python scripts/certify_capability.py lock 51
```
