# Live Test Checklist — Cap 56: news_snapshot
Phase 5 of 6 · Priority: Medium (read_only_network)

## Test 1 — Load news
1. Type: `news`
2. ✅ News headline widget loads
3. ✅ Multiple headlines visible
4. ✅ Sources attributed

## Test 2 — Headlines
1. Type: `top news`
2. ✅ Same headline set or refresh

## Test 3 — News dashboard widget
1. Navigate to the main dashboard (`http://localhost:8000`)
2. ✅ News widget is populated with current headlines

## Sign-off
```
python scripts/certify_capability.py live-signoff 56
python scripts/certify_capability.py lock 56
```
