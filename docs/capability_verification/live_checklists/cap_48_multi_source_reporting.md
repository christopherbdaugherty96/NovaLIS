# Live Test Checklist — Cap 48: multi_source_reporting
Phase 5 of 6 · Priority: Medium (read_only_network)

## Pre-conditions
- [ ] Network available, search API configured

## Test 1 — Research request
1. Type: `research the impact of AI on the job market`
2. ✅ A multi-source report widget appears
3. ✅ Multiple sources listed
4. ✅ Findings section present
5. ✅ Confidence signal visible

## Test 2 — Intelligence brief
1. Type: `create an intelligence brief on electric vehicle adoption`
2. ✅ Structured report returned

## Test 3 — Analyze source reliability
1. Type: `analyze source reliability for Reuters`
2. ✅ Source credibility assessment returned

## Sign-off
```
python scripts/certify_capability.py live-signoff 48
python scripts/certify_capability.py lock 48
```
