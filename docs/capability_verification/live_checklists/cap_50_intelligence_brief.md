# Live Test Checklist — Cap 50: intelligence_brief
Phase 5 of 6 · Priority: Medium (read_only_network)

## Test 1 — Daily brief
1. Type: `give me the daily brief`
2. ✅ Intelligence brief widget returned
3. ✅ Multiple news clusters visible
4. ✅ Brief loads in reasonable time (< 35 seconds)

## Test 2 — Alternative trigger
1. Type: `morning brief`
2. ✅ Same brief returned

## Test 3 — Today's news
1. Type: `today's news`
2. ✅ Current news brief returned

## Test 4 — Expand a cluster
1. After brief loads, type: `expand 1`
2. ✅ Story cluster 1 expands with more detail

## Sign-off
```
python scripts/certify_capability.py live-signoff 50
python scripts/certify_capability.py lock 50
```
